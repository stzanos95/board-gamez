"""
The payload types this gateway can translate.
"""

from fastapi_gateway.products.base_gateway_product import BaseGatewayProduct


class PayloadTypeRegistry:
    """
    What the products served here declare as packable.
    """

    @staticmethod
    def get_type_names(products: tuple[BaseGatewayProduct, ...]) -> tuple[str, ...]:
        """
        The full name of every message a payload may carry.
        """
        return tuple(
            descriptor.full_name
            for product in products
            for file in product.get_payload_files()
            for descriptor in file.message_types_by_name.values()
        )
