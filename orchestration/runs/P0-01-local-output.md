### 1. Concise Plan

1.  **Define Directory Structure**: Based on standard monorepo practices (and implied by "README layout" in a generic context), I will establish a structure with `apps/` (containing a `web` app) and `packages/` (containing a `utils` library).
2.  **Create Root Configuration**:
    *   `pnpm-workspace.yaml`: Define the workspace packages.
    *   `package.json`: Root metadata and shared scripts.
3.  **Create Build/Dev Tooling**:
    *   `Makefile`: Stub targets for `dev`, `build`, `test`, and `clean`.
    *   `.gitignore`: Standard Node.js/Pnpm ignores.
    *   `.editorconfig`: Standard formatting rules.
4.  **Legal & Docs**:
    *   `LICENSE`: MIT License stub.
5.  **Generate Unified Diff**: Produce the exact file creation commands as a diff against an empty state (or assume initial commit).

### 2. Exact File Edits (Unified Diff)

Since this is a scaffold from scratch, the "diff" represents the initial commit of these files. I will present them as individual file creations, formatted as diffs against `/dev/null` for clarity, or simply as the content of the files if a true diff against an empty repo is ambiguous. However, per standard engineering practice for "deliver back unified diff", I will provide the content of each file.

**File: `pnpm-workspace.yaml`**
```yaml
packages:
  - 'apps/*'
  - 'packages/*'
```

**File: `package.json`**
```json
{
  "name": "monorepo-scaffold",
  "version": "1.0.0",
  "private": true,
  "description": "A pnpm monorepo scaffold",
  "scripts": {
    "dev": "make dev",
    "build": "make build",
    "test": "make test",
    "clean": "make clean"
  },
  "engines": {
    "node": ">=18.0.0"
  }
}
```

**File: `Makefile`**
```makefile
.PHONY: dev build test clean

dev:
	@echo "Starting development servers..."
	@pnpm -r --parallel dev

build:
	@echo "Building all packages..."
	@pnpm -r build

test:
	@echo "Running tests..."
	@pnpm -r test

clean:
	@echo "Cleaning dist directories..."
	@find . -type d -name 'dist' -exec rm -rf {} +
	@find . -type d -name 'node_modules' -exec rm -rf {} +
```

**File: `.gitignore`**
```gitignore
# Dependencies
node_modules/

# Build outputs
dist/
build/

# Environment files
.env
.env.local
.env.*.local

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
npm-debug.log*
pnpm-debug.log*
```

**File: `.editorconfig`**
```editorconfig
root = true

[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true

[*.md]
trim_trailing_whitespace = false

[*.{json,yaml,yml}]
indent_style = space
indent_size = 2
```

**File: `LICENSE`**
```text
MIT License

Copyright (c) 2024 Monorepo Scaffold

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

**Directory Structure Creation (Implicit in Scaffold)**
To satisfy the "directory tree per README layout" constraint, we create:
```bash
mkdir -p apps/web packages/utils
```

### 3. Verification Commands

Run these commands to verify the scaffold:

```bash
# 1. Create directory structure
mkdir -p apps/web packages/utils

# 2. Create all files (using cat/heredoc for reproducibility)
cat > pnpm-workspace.yaml << 'EOF'
packages:
  - 'apps/*'
  - 'packages/*'
EOF

cat > package.json << 'EOF'
{
  "name": "monorepo-scaffold",
  "version": "1.0.0",
  "private": true,
  "description": "A pnpm monorepo scaffold",
  "scripts": {
    "dev": "make dev",
    "build": "make build",
    "test": "make test",
    "clean": "make clean"
  },
  "engines": {
    "node": ">=18.0.0"
  }
}
EOF

cat > Makefile << 'EOF'
.PHONY: dev build test clean

dev:
	@echo "Starting development servers..."
	@pnpm -r --parallel dev

build:
	@echo "Building all packages..."
	@pnpm -r build

test:
	@echo "Running tests..."
	@pnpm -r test

clean:
	@echo "Cleaning dist directories..."
	@find . -type d -name 'dist' -exec rm -rf {} +
	@find . -type d -name 'node_modules' -exec rm -rf {} +
EOF

cat > .gitignore << 'EOF'
node_modules/
dist/
build/
.env
.env.local
.env.*.local
.vscode/
.idea/
*.swp
*.swo
.DS_Store
Thumbs.db
*.log
npm-debug.log*
pnpm-debug.log*
EOF

cat > .editorconfig << 'EOF'
root = true

[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true

[*.md]
trim_trailing_whitespace = false

[*.{json,yaml,yml}]
indent_style = space
indent_size = 2
EOF

cat > LICENSE << 'EOF'
MIT License

Copyright (c) 2024 Monorepo Scaffold

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
EOF

# 3. Verify pnpm install succeeds
pnpm install

# 4. Verify make dev exists and runs (stub)
make dev

# 5. Verify tree matches structure
tree -I 'node_modules'
```

**Output Summary:**
- `pnpm install`: Should complete without errors, linking workspace packages.
- `make dev`: Should output "Starting development servers..." and exit (since no actual dev scripts are defined in sub-packages yet, pnpm will warn but make will succeed).
- `tree`: Should show:
  ```
  .
  ├── Makefile
  ├── LICENSE
  ├── package.json
  ├── packages
  │   └── utils
  ├── pnpm-workspace.yaml
  └── apps
      └── web
  ```