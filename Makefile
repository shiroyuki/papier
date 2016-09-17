IMAGE_TAG=shiroyuki/papier
WORKDIR=/opt/shiroyuki/papier
SAMPLE_DIR=$$(pwd)/sample-site

image-build:
	@docker build -t $(IMAGE_TAG) .

image-push: image-build
	@docker push $(IMAGE_TAG)

dev-setup:
	npm install

css:
	node_modules/node-sass/bin/node-sass \
		-rq \
		--output-stype compressed \
		--follow \
		-o papier/template \
		papier/template

css-live:
	node_modules/node-sass/bin/node-sass \
		-r \
		--watch \
		--output-stype compressed \
		--follow \
		-o papier/template \
		papier/template

term:
	@docker run \
		-it --rm \
		-u $$UID \
		-v $$(pwd):$(WORKDIR) \
		--privileged \
		-w $(WORKDIR) \
		$(IMAGE_TAG) \
		bash

run-sample-danbo:
	bin/papier build -s ../com.shiroyuki.www/r15/src -o ../com.shiroyuki.www/r15/build #-w

test-term: image-build
	@rm -rf $(SAMPLE_DIR)/build/* || echo '(Already deleted sample files)'
	@rm -rf $(SAMPLE_DIR)/.papier-cache/* || echo '(Already deleted cache)'
	@docker run \
		-it --rm \
		-u $$UID \
		-v $(SAMPLE_DIR):/data \
		--privileged \
		-w /data \
		$(IMAGE_TAG) \
		papier compile -s src -o build

http-sample:
	@cd sample-site/build && python3 -m http.server --cgi 8000
