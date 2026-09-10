# syntax=docker/dockerfile:1

# The build context is the repository ROOT, not this directory. The TypeScript
# side is one npm workspace rooted there, and this deployable is one member of
# it. infra/compose/docker-compose.yml sets that context.

# Pinned to the same image scripts/_shared.sh runs, so a bundle built here and a
# bundle built on a workstation come from one toolchain.
FROM node:22-alpine AS builder

WORKDIR /repo

# Every manifest in the workspace, and nothing else, so a change to the
# application does not reinstall the dependency set.
COPY package.json package-lock.json ./
COPY idl/contracts/gen/typescript/package.json idl/contracts/gen/typescript/
COPY packages/ux/package.json packages/ux/
COPY deployables/gamez-ux/package.json deployables/gamez-ux/
RUN npm ci --no-audit --no-fund

COPY idl/contracts/gen/typescript idl/contracts/gen/typescript
COPY packages/ux packages/ux
COPY deployables/gamez-ux deployables/gamez-ux

# Type-checks before it bundles, so a type error fails the image rather than
# shipping in it.
RUN npm run build --workspace gamez-ux


FROM nginx:1.27-alpine AS runtime

COPY --from=builder /repo/deployables/gamez-ux/dist /usr/share/nginx/html
COPY deployables/gamez-ux/docker/nginx.conf /etc/nginx/conf.d/default.conf
COPY deployables/gamez-ux/docker/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

# Documentation only, and it must match the port nginx.conf listens on.
EXPOSE 8081

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["serve"]
