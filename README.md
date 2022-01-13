# dockerfile_ast
Python library for generating abstract syntax tree (AST) of Dockerfile.

## NOTES
This repository is incomplete.

## Installation
This project partly uses ["dockerfile" package](https://pypi.org/project/dockerfile/)
(maintained by [asottile](https://pypi.org/user/asottile/)).
You need to install Go because "dockerfile" package is written by Go Language.
You can download Go via https://go.dev/dl/.
### From Git
```bash
git clone https://github.com/gruidae/dockerfile_ast.git
cd dockerfile_ast
python3 -m pip install .
```

### Usage
#### Parse Dockerfile from text
```python
from dockerfile_ast import DockerfileAST, DockerfileASTVisitor, DockerfileParser

dockerfile_src = """FROM ubuntu
RUN set -ex \\
  && apt-get update \\
  && apt-get install -y --no-install-recommends httpd \\
  && rm -rf /var/lib/apt/lists/*
EXPOSE 80
ENTRYPOINT ["httpd"]
"""

# parse Dockerfile
dockerfile_parser = DockerfileParser()
dfile_ast = dockerfile_parser.parse(dockerfile_src)

# visit nodes in Dockerfile AST
visitor = DockerfileASTVisitor(dfile_ast)
visitor.visit()
```

#### Parse Dockerfile from file
```python
from dockerfile_ast import DockerfileAST, DockerfileASTVisitor, DockerfileParser

# parse Dockerfile
dockerfile_parser = DockerfileParser()
dfile_ast = dockerfile_parser.parse_file("data/foo/Dockerfile")

# visit nodes in Dockerfile AST
visitor = DockerfileASTVisitor(dfile_ast)
visitor.visit()
```
