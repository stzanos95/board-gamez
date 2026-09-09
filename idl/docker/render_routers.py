"""
Write one FastAPI router module per service in an OpenAPI document.

Reads the document protoc-gen-openapi produced and writes, for each service tag,
an abstract base declaring one method per operation and a router class binding
every path to an instance of it. The generated modules hold no behaviour: an
implementation lives in the domain package that owns the service.

Model classes are not written here. They come from datamodel-code-generator, and
a schema named `idl.lobby.dto.UpsertTableRequest` lands as `UpsertTableRequest`
in the module `idl.lobby.dto` under the root package.
"""

import argparse
import json
import re
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

import yaml

FILE_ENCODING = "utf-8"
SCHEMA_REFERENCE_PREFIX = "#/components/schemas/"
OPERATION_ID_SEPARATOR = "_"
JSON_CONTENT_TYPE = "application/json"
SUCCESS_STATUS = "200"
DEFAULT_STATUS = "default"
MODULE_SEPARATOR = "."
PATH_SEPARATOR = "/"
PYTHON_SUFFIX = ".py"
INDENT = "    "
MAXIMUM_LINE_LENGTH = 100

PYTHON_TYPES_BY_SCHEMA_TYPE = {
    "string": "str",
    "boolean": "bool",
    "integer": "int",
    "number": "float",
}


class DocumentError(Exception):
    """
    The document is not the shape this renderer knows how to read.
    """


class HttpMethod(StrEnum):
    """
    The methods an operation may be declared under.
    """

    GET = "get"
    POST = "post"
    PUT = "put"
    PATCH = "patch"
    DELETE = "delete"


class ParameterLocation(StrEnum):
    """
    Where an operation reads a parameter from.
    """

    PATH = "path"
    QUERY = "query"


@dataclass(frozen=True, slots=True)
class ImportedType:
    """
    A generated model class, and the module it is imported from.
    """

    module: str
    name: str


@dataclass(frozen=True, slots=True)
class ParameterSpec:
    """
    One path or query parameter.

    `wire_name` is what the URL carries and what the handler signature must be
    written under; `python_name` is what the implementation is called with.
    """

    wire_name: str
    python_name: str
    location: ParameterLocation
    required: bool
    python_type: str


@dataclass(frozen=True, slots=True)
class OperationSpec:
    """
    One path, and the method it answers on.
    """

    method: HttpMethod
    path: str
    operation_id: str
    handler_name: str
    parameters: tuple[ParameterSpec, ...]
    request: ImportedType | None
    response: ImportedType
    error_response: ImportedType | None


@dataclass(frozen=True, slots=True)
class ServiceSpec:
    """
    Every operation carrying one service's tag.
    """

    tag: str
    module_name: str
    base_class_name: str
    router_class_name: str
    operations: tuple[OperationSpec, ...]


class Node:
    """
    Typed reads of a parsed YAML document, each naming what it was reading.
    """

    @staticmethod
    def mapping(value: object, context: str) -> dict[str, object]:
        if not isinstance(value, dict):
            raise DocumentError(
                f"{context}: expected a mapping, got {type(value).__name__}"
            )
        return {str(key): item for key, item in value.items()}

    @staticmethod
    def sequence(value: object, context: str) -> list[object]:
        if not isinstance(value, list):
            raise DocumentError(
                f"{context}: expected a list, got {type(value).__name__}"
            )
        return value

    @staticmethod
    def text(value: object, context: str) -> str:
        if not isinstance(value, str):
            raise DocumentError(
                f"{context}: expected a string, got {type(value).__name__}"
            )
        return value

    @staticmethod
    def flag(value: object, context: str, default: bool) -> bool:
        if value is None:
            return default
        if not isinstance(value, bool):
            raise DocumentError(f"{context}: expected true or false, got {value!r}")
        return value


class Naming:
    """
    The names the generated modules and classes are known by.
    """

    _BOUNDARY = re.compile(r"(?<=[a-z0-9])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])")

    @staticmethod
    def to_snake_case(name: str) -> str:
        return Naming._BOUNDARY.sub("_", name).lower()

    @staticmethod
    def handler_name(operation_id: str) -> str:
        """
        The method name for an operation id such as `TableService_ReadTable`.
        """
        _, separator, method_name = operation_id.partition(OPERATION_ID_SEPARATOR)
        return Naming.to_snake_case(method_name if separator else operation_id)

    @staticmethod
    def module_name(tag: str) -> str:
        return Naming.to_snake_case(tag)

    @staticmethod
    def base_class_name(tag: str) -> str:
        return f"Base{tag}"

    @staticmethod
    def router_class_name(tag: str) -> str:
        return f"{tag}Router"


class SchemaReference:
    """
    Where a `$ref` lands once datamodel-code-generator has written the models.
    """

    @staticmethod
    def to_imported_type(reference: str, root_package: str) -> ImportedType:
        """
        Turn `#/components/schemas/idl.lobby.dto.Table` into its module and class.

        Requires fully qualified schema names, which is what the document is
        generated with. A name carrying no package would collide with any other
        domain declaring it.
        """
        if not reference.startswith(SCHEMA_REFERENCE_PREFIX):
            raise DocumentError(
                f"only component schema references are supported, got {reference!r}"
            )
        qualified_name = reference[len(SCHEMA_REFERENCE_PREFIX) :]
        package, separator, class_name = qualified_name.rpartition(MODULE_SEPARATOR)
        if not separator:
            raise DocumentError(
                f"schema {qualified_name!r} is not fully qualified; "
                f"generate the document with fq_schema_naming=true"
            )
        for segment in [*package.split(MODULE_SEPARATOR), class_name]:
            if not segment.isidentifier():
                raise DocumentError(
                    f"schema {qualified_name!r} has a segment that is not a name"
                )
        return ImportedType(
            module=f"{root_package}{MODULE_SEPARATOR}{package}", name=class_name
        )


class DocumentReader:
    """
    Reading services out of an OpenAPI document.
    """

    @staticmethod
    def read_services(
        document_path: Path, root_package: str
    ) -> tuple[ServiceSpec, ...]:
        """
        Every service in the document, in a stable order.

        Raises DocumentError for any operation shape the renderer cannot write,
        rather than emitting a router that quietly drops part of the contract.
        """
        document = Node.mapping(
            yaml.safe_load(document_path.read_text(encoding=FILE_ENCODING)),
            str(document_path),
        )
        paths = Node.mapping(document.get("paths", {}), "paths")
        operations_by_tag: dict[str, list[OperationSpec]] = {}
        for path, path_item in sorted(paths.items()):
            for method_name, operation in sorted(Node.mapping(path_item, path).items()):
                tag, specification = DocumentReader._read_operation(
                    path=path,
                    method_name=method_name,
                    operation=Node.mapping(operation, f"{path}.{method_name}"),
                    root_package=root_package,
                )
                operations_by_tag.setdefault(tag, []).append(specification)
        return tuple(
            ServiceSpec(
                tag=tag,
                module_name=Naming.module_name(tag),
                base_class_name=Naming.base_class_name(tag),
                router_class_name=Naming.router_class_name(tag),
                operations=tuple(operations),
            )
            for tag, operations in sorted(operations_by_tag.items())
        )

    @staticmethod
    def _read_operation(
        path: str, method_name: str, operation: dict[str, object], root_package: str
    ) -> tuple[str, OperationSpec]:
        context = f"{method_name.upper()} {path}"
        if method_name not in set(HttpMethod):
            raise DocumentError(f"{context}: unsupported method")
        tags = Node.sequence(operation.get("tags", []), f"{context}.tags")
        if len(tags) != 1:
            raise DocumentError(
                f"{context}: expected exactly one tag naming the service, got {tags!r}"
            )
        operation_id = Node.text(operation.get("operationId"), f"{context}.operationId")
        return Node.text(tags[0], f"{context}.tags"), OperationSpec(
            method=HttpMethod(method_name),
            path=path,
            operation_id=operation_id,
            handler_name=Naming.handler_name(operation_id),
            parameters=DocumentReader._read_parameters(operation, context),
            request=DocumentReader._read_request(operation, context, root_package),
            response=DocumentReader._read_response(
                operation, context, root_package, SUCCESS_STATUS
            ),
            error_response=DocumentReader._read_optional_response(
                operation, context, root_package, DEFAULT_STATUS
            ),
        )

    @staticmethod
    def _read_parameters(
        operation: dict[str, object], context: str
    ) -> tuple[ParameterSpec, ...]:
        parameters = []
        for entry in Node.sequence(
            operation.get("parameters", []), f"{context}.parameters"
        ):
            parameter = Node.mapping(entry, f"{context}.parameters")
            wire_name = Node.text(parameter.get("name"), f"{context}.parameters.name")
            location = Node.text(
                parameter.get("in"), f"{context}.parameters.{wire_name}.in"
            )
            if location not in set(ParameterLocation):
                raise DocumentError(
                    f"{context}: parameter {wire_name!r} is read from {location!r}, "
                    f"and only {', '.join(sorted(ParameterLocation))} are supported"
                )
            schema = Node.mapping(
                parameter.get("schema"), f"{context}.parameters.{wire_name}.schema"
            )
            schema_type = Node.text(
                schema.get("type"), f"{context}.parameters.{wire_name}.schema.type"
            )
            python_type = PYTHON_TYPES_BY_SCHEMA_TYPE.get(schema_type)
            if python_type is None:
                raise DocumentError(
                    f"{context}: parameter {wire_name!r} is a {schema_type!r}, and only "
                    f"{', '.join(sorted(PYTHON_TYPES_BY_SCHEMA_TYPE))} are supported"
                )
            parameters.append(
                ParameterSpec(
                    wire_name=wire_name,
                    python_name=Naming.to_snake_case(wire_name),
                    location=ParameterLocation(location),
                    required=Node.flag(
                        parameter.get("required"),
                        f"{context}.parameters.{wire_name}.required",
                        False,
                    ),
                    python_type=python_type,
                )
            )
        return tuple(parameters)

    @staticmethod
    def _read_request(
        operation: dict[str, object], context: str, root_package: str
    ) -> ImportedType | None:
        body = operation.get("requestBody")
        if body is None:
            return None
        return DocumentReader._read_json_schema(
            Node.mapping(body, f"{context}.requestBody"),
            f"{context}.requestBody",
            root_package,
        )

    @staticmethod
    def _read_response(
        operation: dict[str, object], context: str, root_package: str, status: str
    ) -> ImportedType:
        response = DocumentReader._read_optional_response(
            operation, context, root_package, status
        )
        if response is None:
            raise DocumentError(f"{context}: no {status} response with a JSON body")
        return response

    @staticmethod
    def _read_optional_response(
        operation: dict[str, object], context: str, root_package: str, status: str
    ) -> ImportedType | None:
        responses = Node.mapping(operation.get("responses", {}), f"{context}.responses")
        response = responses.get(status)
        if response is None:
            return None
        return DocumentReader._read_json_schema(
            Node.mapping(response, f"{context}.responses.{status}"),
            f"{context}.responses.{status}",
            root_package,
        )

    @staticmethod
    def _read_json_schema(
        holder: dict[str, object], context: str, root_package: str
    ) -> ImportedType | None:
        content = Node.mapping(holder.get("content", {}), f"{context}.content")
        media_type = content.get(JSON_CONTENT_TYPE)
        if media_type is None:
            return None
        schema = Node.mapping(
            Node.mapping(media_type, f"{context}.{JSON_CONTENT_TYPE}").get("schema"),
            f"{context}.schema",
        )
        return SchemaReference.to_imported_type(
            Node.text(schema.get("$ref"), f"{context}.schema.$ref"), root_package
        )


class ModuleRenderer:
    """
    Turning one service into the text of its module.
    """

    @staticmethod
    def render(service: ServiceSpec, root_package: str) -> str:
        lines = [
            '"""',
            f"{service.tag}, generated from the OpenAPI document. Do not edit.",
            "",
            f"{service.base_class_name} declares one method per operation, and",
            f"{service.router_class_name}.build binds every path to an instance of it. The",
            "implementation belongs to the domain package that owns this service.",
            '"""',
            "",
            "from abc import ABC, abstractmethod",
            "",
            "from fastapi import APIRouter",
            "",
        ]
        lines.extend(ModuleRenderer._render_model_imports(service))
        lines.extend(
            ["", "", f"SERVICE_TAG = {ModuleRenderer._quoted(service.tag)}", "", ""]
        )
        lines.extend(ModuleRenderer._render_base_class(service))
        lines.extend(["", ""])
        lines.extend(ModuleRenderer._render_router_class(service))
        return "\n".join(lines) + "\n"

    @staticmethod
    def _quoted(text: str) -> str:
        """
        A double-quoted literal, escaped the way Python and JSON agree on.
        """
        return json.dumps(text)

    @staticmethod
    def _render_model_imports(service: ServiceSpec) -> list[str]:
        names_by_module: dict[str, set[str]] = {}
        for operation in service.operations:
            for imported in (
                operation.request,
                operation.response,
                operation.error_response,
            ):
                if imported is not None:
                    names_by_module.setdefault(imported.module, set()).add(
                        imported.name
                    )
        lines = []
        for module, names in sorted(names_by_module.items()):
            single_line = f"from {module} import {', '.join(sorted(names))}"
            if len(single_line) <= MAXIMUM_LINE_LENGTH:
                lines.append(single_line)
                continue
            lines.append(f"from {module} import (")
            lines.extend(f"{INDENT}{name}," for name in sorted(names))
            lines.append(")")
        return lines

    @staticmethod
    def _render_base_class(service: ServiceSpec) -> list[str]:
        lines = [
            f"class {service.base_class_name}(ABC):",
            f'{INDENT}"""',
            f"{INDENT}What an implementation of {service.tag} must answer.",
            f'{INDENT}"""',
        ]
        for operation in service.operations:
            lines.extend(
                [
                    "",
                    f"{INDENT}@abstractmethod",
                    f"{INDENT}async def {operation.handler_name}(",
                    f"{INDENT * 2}self,",
                ]
            )
            for declaration in ModuleRenderer._signature_declarations(
                operation, wire_names=False
            ):
                lines.append(f"{INDENT * 2}{declaration},")
            lines.extend(
                [
                    f"{INDENT}) -> {operation.response.name}:",
                    f'{INDENT * 2}"""',
                    f"{INDENT * 2}{operation.method.upper()} {operation.path}",
                    f'{INDENT * 2}"""',
                ]
            )
        return lines

    @staticmethod
    def _render_router_class(service: ServiceSpec) -> list[str]:
        lines = [
            f"class {service.router_class_name}:",
            f'{INDENT}"""',
            f"{INDENT}The paths {service.tag} declares, bound to an implementation.",
            f'{INDENT}"""',
            "",
            f"{INDENT}@staticmethod",
            f"{INDENT}def build(service: {service.base_class_name}) -> APIRouter:",
            f'{INDENT * 2}"""',
            f"{INDENT * 2}A router answering every {service.tag} path through `service`.",
            f'{INDENT * 2}"""',
            f"{INDENT * 2}router = APIRouter(tags=[SERVICE_TAG])",
        ]
        for operation in service.operations:
            lines.extend(ModuleRenderer._render_operation(operation))
        lines.extend(["", f"{INDENT * 2}return router"])
        return lines

    @staticmethod
    def _render_operation(operation: OperationSpec) -> list[str]:
        decorator = [
            "",
            f"{INDENT * 2}@router.{operation.method.value}(",
            f"{INDENT * 3}{ModuleRenderer._quoted(operation.path)},",
            f"{INDENT * 3}operation_id={ModuleRenderer._quoted(operation.operation_id)},",
            f"{INDENT * 3}response_model={operation.response.name},",
            # A proto3 field that was never set is absent from the JSON, not
            # null: the schema this document declares has no nullable types.
            f"{INDENT * 3}response_model_exclude_none=True,",
        ]
        if operation.error_response is not None:
            decorator.append(
                f"{INDENT * 3}responses={{{ModuleRenderer._quoted(DEFAULT_STATUS)}: "
                f'{{"model": {operation.error_response.name}}}}},'
            )
        decorator.append(f"{INDENT * 2})")

        signature = [f"{INDENT * 2}async def {operation.handler_name}("]
        for declaration in ModuleRenderer._signature_declarations(
            operation, wire_names=True
        ):
            signature.append(f"{INDENT * 3}{declaration},")
        signature.append(f"{INDENT * 2}) -> {operation.response.name}:")

        arguments = [
            f"{INDENT * 4}{parameter.python_name}={parameter.wire_name},"
            for parameter in ModuleRenderer._ordered_parameters(operation)
        ]
        if operation.request is not None:
            arguments.insert(
                len(
                    [
                        p
                        for p in ModuleRenderer._ordered_parameters(operation)
                        if p.required
                    ]
                ),
                f"{INDENT * 4}request=request,",
            )
        call = [
            f"{INDENT * 3}return await service.{operation.handler_name}(",
            *arguments,
            f"{INDENT * 3})",
        ]
        return [*decorator, *signature, *call]

    @staticmethod
    def _ordered_parameters(operation: OperationSpec) -> list[ParameterSpec]:
        """
        Required parameters first, since an optional one carries a default.
        """
        return [
            *[parameter for parameter in operation.parameters if parameter.required],
            *[
                parameter
                for parameter in operation.parameters
                if not parameter.required
            ],
        ]

    @staticmethod
    def _signature_declarations(
        operation: OperationSpec, wire_names: bool
    ) -> list[str]:
        """
        The parameters of one handler, in an order Python accepts.

        The router's own handler must name a path parameter exactly as the path
        spells it, which is why the two sides are rendered differently.
        """
        declarations = []
        ordered = ModuleRenderer._ordered_parameters(operation)
        for parameter in ordered:
            if not parameter.required:
                continue
            name = parameter.wire_name if wire_names else parameter.python_name
            declarations.append(f"{name}: {parameter.python_type}")
        if operation.request is not None:
            declarations.append(f"request: {operation.request.name}")
        for parameter in ordered:
            if parameter.required:
                continue
            name = parameter.wire_name if wire_names else parameter.python_name
            declarations.append(f"{name}: {parameter.python_type} | None = None")
        return declarations


class RouterWriter:
    """
    Writing the rendered modules into the generated package.
    """

    @staticmethod
    def write_all(document_path: Path, output_dir: Path, root_package: str) -> int:
        """
        Write one module per service, and the package that holds them.

        Returns how many services were written.
        """
        services = DocumentReader.read_services(document_path, root_package)
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "__init__.py").write_text("", encoding=FILE_ENCODING)
        for service in services:
            destination = output_dir / f"{service.module_name}{PYTHON_SUFFIX}"
            destination.write_text(
                ModuleRenderer.render(service, root_package), encoding=FILE_ENCODING
            )
            print(f"  router      -> {service.tag} ({destination.name})")
        return len(services)


def main() -> int:
    """
    The console entry point, which must be a module-level function.
    """
    parser = argparse.ArgumentParser(
        description="Render FastAPI routers from an OpenAPI document."
    )
    parser.add_argument("--document", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--root-package", required=True)
    arguments = parser.parse_args()
    written = RouterWriter.write_all(
        arguments.document, arguments.output, arguments.root_package
    )
    if written == 0:
        print("  router      -> no services in the document")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
