# Tamanna Response Engine
class ResponseEngine:
    def respond(self, query):
        responses = {
            "status": "System is running",
            "backup": "Backup initiated",
            "error": "Fixing missing code...",
        }
        return responses.get(query, "Unknown command")


if __name__ == "__main__":
    engine = ResponseEngine()
    print(engine.respond("status"))
    print(engine.respond("backup"))
