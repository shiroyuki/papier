## Default settings

```yaml
papier:
    source: # (required)
        path: src # (required)
        index_filename: index # the default filename of the index page (default, optional)
    theme: ~ # primary theme NOTE use the built-in theme (optional)
    output:
        path: build
```

Alternatively, to refer to the built-in theme, the `theme` section can be
referred as:

```yaml
papier:
    # ... (omitted) ...
    theme:
        path: ~
```

## Customize your site

### Use your own custom theme for the whole site.

```yaml
papier:
    # ... (omitted) ...
    theme:
        path: themes # the absolute path or path relative to the config file (required)
        layout: default # the name of the main template file (default, optional)
```

### Customization per path or page

```yaml
papier:
    # ... (omitted) ...
    override:
        # NOTE all pages under /projects
        /projects/*:
            path: project # the absolute path or path relative to the config file (required)
            layout: default # the name of the layout file
        # NOTE all pages under /articles
        /articles/*:
            path: journal # the absolute path or path relative to the config file (required)
            layout: default # the name of the layout file
        # NOTE only the index page
        /index.html:
            path: themes # the absolute path or path relative to the config file (required)
            layout: default # the name of the layout file
```
