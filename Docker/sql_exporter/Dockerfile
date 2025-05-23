FROM golang:1.20-alpine as builder

RUN apk add --no-cache git make

WORKDIR /src
RUN git clone --depth=1 https://github.com/prometheus-community/sql_exporter.git .
RUN make build

FROM alpine:latest
COPY --from=builder /src/sql_exporter /bin/sql_exporter
COPY sql_exporter.yml /config/sql_exporter.yml
COPY mssql_standard.collector.yml /config/mssql_standard.collector.yml

ENTRYPOINT ["/bin/sql_exporter", "--config.file=/config/sql_exporter.yml"]
