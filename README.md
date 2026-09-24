<img src="https://raw.githubusercontent.com/GrahamDumpleton/autowrapt/develop/assets/autowrapt-logo.svg" alt="autowrapt" width="240">

# autowrapt

Bootstrap mechanism for monkey patches.

autowrapt triggers the monkey patching of a Python application at
interpreter startup, without the application itself being modified. It is a
small companion to [wrapt](https://github.com/GrahamDumpleton/wrapt), whose
post import hook mechanism does the actual work. You write the patches as
post import hooks, expose them as entry points, and name the entry point
group in an environment variable when running the application.

## Installation

```console
pip install autowrapt
```

autowrapt must be installed into the same Python installation or virtual
environment as the application it is to patch. Installing it puts a
`autowrapt-init.pth` file at the top of site-packages, which is what
triggers it at interpreter startup.

## Usage

Write a post import hook for each module you want to patch. It is a
function which takes the module as its only argument and is called
immediately after the module is first imported.

```python
# mycompany/patches.py

import wrapt


def patch_requests(module):
    @wrapt.wrap_function_wrapper(module, "get")
    def wrapper(wrapped, instance, args, kwargs):
        print("GET", args[0] if args else kwargs.get("url"))

        return wrapped(*args, **kwargs)
```

Register the hooks as entry points in the package which contains them. The
entry point group name is yours to choose, and within it each entry point
name is the module the hook is for.

```toml
# pyproject.toml

[project.entry-points."mycompany.patches"]
requests = "mycompany.patches:patch_requests"
```

Run the application with the `AUTOWRAPT_BOOTSTRAP` environment variable set
to the name of the entry point group.

```console
AUTOWRAPT_BOOTSTRAP=mycompany.patches python app.py
```

More than one group can be named, separated by commas. Every entry point in
each group is registered as a post import hook, and each hook runs when, and
only when, its module is first imported. A module which is never imported
costs nothing. When the variable is not set, nothing from autowrapt is
imported at all.

## Example

The package ships one example hook, registered under the
`autowrapt.examples` group against the `this` module.

```console
AUTOWRAPT_BOOTSTRAP=autowrapt.examples python -c "import this"
```

This prints the Zen of Python as normal, with one extra line added at the
end.

## How it works

The `.pth` file is processed by the `site` module while the interpreter
starts up. Its single line imports `autowrapt.bootstrap` and calls
`bootstrap()`, but only when `AUTOWRAPT_BOOTSTRAP` is set.

Because `.pth` files are processed part way through site initialisation,
before the module search path is complete, `bootstrap()` does not register
the hooks straight away. It arranges for that to happen as the last step of
site initialisation instead, after the `sitecustomize` module, or the
`usercustomize` module when support for that is enabled, has been loaded.
Only then is wrapt imported and asked to discover the entry points in each
named group.

## Limitations

- autowrapt has to be installed in the same environment as the
  application. A wrapper script run from one environment cannot patch a
  Python program run from another.

- Nothing happens when Python is run with the `-S` option, or in an
  embedded interpreter which does not run the `site` module, since the
  `.pth` file is never processed.

- Installers which do not honour files at the root of a wheel, or tools
  which build environments without processing `.pth` files, will not
  trigger autowrapt.

## Documentation

The post import hook mechanism autowrapt builds on is described in the
monkey patching section of the
[wrapt documentation](https://wrapt.readthedocs.io/). Documentation for
autowrapt itself is also being added there, since the two are bound up
together.

[wrapture](https://github.com/GrahamDumpleton/wrapture), a higher level
monkey patching, testing and tracing library built on wrapt, uses autowrapt
for zero-code injection of its own patches.

## License

BSD 2-Clause. See [LICENSE](LICENSE).
