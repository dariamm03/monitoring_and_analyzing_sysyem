docker build --no-cache -f App/Dockerfile.App -t flexberrysamplelogging/app ../

docker build --no-cache -f Postgres/Dockerfile.PostgreSql -t flexberrysamplelogging/postgre-sql ../SQL

docker build --no-cache -f GrafanaLoki/Dockerfile.Loki -t flexberrysamplelogging/loki .

docker build --no-cache -f Promtail/Dockerfile.Promtail -t flexberrysamplelogging/promtail .