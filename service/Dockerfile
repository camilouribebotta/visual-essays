FROM python:3.8

ENV APT_KEY_DONT_WARN_ON_DANGEROUS_USAGE=DontWarn

RUN set -e; \
    apt-get update; \
    apt-get install -y --no-install-recommends tini; \
    apt-get clean; \
    rm -rf /var/tmp/* /tmp/* /var/lib/apt/lists/*

RUN set -e; \
    pip install sqlitedict flask requests uwsgi Markdown pygments pymdown-extensions markdown markdown-captions bs4 html5 python-slugify rdflib rdflib-jsonld PyLD expiringdict google-cloud google-auth google-cloud-storage 

WORKDIR /usr/src/app

ADD src src
ADD mappings mappings
ADD index.html .
ADD gh-token .
COPY favicon.ico src/static/favicon.ico

ENV PORT 8080

ENTRYPOINT ["tini", "--"]
CMD uwsgi --http :${PORT} --manage-script-name --mount /app=src.app:app --enable-threads --processes 4