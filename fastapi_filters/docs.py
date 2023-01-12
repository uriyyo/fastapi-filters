from fastapi import FastAPI


def fix_docs(app: FastAPI) -> None:
    def _fix_docs() -> None:
        openapi = app.openapi()

        for endpoints in openapi["paths"].values():
            for endpoint in endpoints.values():
                for parameter in endpoint.get("parameters", ()):
                    if "explode" in parameter["schema"]:
                        parameter["explode"] = parameter["schema"].pop("explode")

    app.add_event_handler("startup", _fix_docs)


__all__ = [
    "fix_docs",
]
