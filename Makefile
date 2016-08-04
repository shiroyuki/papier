IMAGE_TAG=shiroyuki/papier
WORKDIR=/opt/shiroyuki/papier
SAMPLE_DIR=$$(pwd)/sample-site

build-image:
	@docker build -t $(IMAGE_TAG) .

term:
	@docker run \
		-it --rm \
		-u $$UID \
		-v $$(pwd):$(WORKDIR) \
		--privileged \
		-w $(WORKDIR) \
		$(IMAGE_TAG) \
		bash

test-term: build-image
	@rm -rf $(SAMPLE_DIR)/build || echo '(Already deleted sample files)'
	@docker run \
		-it --rm \
		-u $$UID \
		-v $(SAMPLE_DIR):/data \
		--privileged \
		-w /data \
		$(IMAGE_TAG) \
		papier compile -s src -o build
