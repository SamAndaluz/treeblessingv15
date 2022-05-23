FROM odoo:12.0
USER root
RUN pip3 install wheel
RUN set -x; \
	pip3 install pagseguro


CMD ["odoo","--dev=all"]
