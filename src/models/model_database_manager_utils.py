"""
Automatically extracted utility functions
"""


# get_model_database_manager
def get_model_database_manager() -> ModelDatabaseManager:
    """Factory function pour obtenir une instance du gestionnaire"""
    return ModelDatabaseManager()


# get_supported_models_for_tools
def get_supported_models_for_tools(tool_names: List[str]) -> Dict[str, List[ModelInfo]]:
    """Récupère les modèles supportés pour plusieurs outils"""
    manager = get_model_database_manager()
    result: Dict[str, List[ModelInfo]] = {}

    for tool_name in tool_names:
        result[tool_name] = manager.get_supported_models_for_tool(tool_name)

    return result
