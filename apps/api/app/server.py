from __future__ import annotations

import uvicorn

from .main import create_app


def main() -> None:
    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=app.state.settings.port if hasattr(app.state, "settings") else 8081)


if __name__ == "__main__":
    main()
