submit:
	curl -X POST https://api.github.com/repos/clgi-technology/volunteer-submit-form/dispatches \
	-H "Authorization: Bearer $(GITHUB_TOKEN)" \
	-H "Accept: application/vnd.github.everest-preview+json" \
	-H "Content-Type: application/json" \
	-d @payload.json
