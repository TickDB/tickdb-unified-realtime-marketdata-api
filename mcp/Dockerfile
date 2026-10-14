FROM python:3.12-slim

WORKDIR /app

ARG RELEASE_VERSION=0.2.3
ARG VCS_REF=unknown
LABEL org.opencontainers.image.version="$RELEASE_VERSION" \
      org.opencontainers.image.revision="$VCS_REF"

COPY pyproject.toml .
COPY tickdb_mcp/ tickdb_mcp/
COPY main.py .
RUN pip install --no-cache-dir .

ENV MCP_TRANSPORT=streamable-http
ENV MCP_HOST=0.0.0.0
ENV MCP_PORT=8000

EXPOSE 8000

CMD ["python", "main.py"]
