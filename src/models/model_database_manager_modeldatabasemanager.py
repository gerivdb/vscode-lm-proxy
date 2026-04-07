"""
Automatically extracted ModelDatabaseManager class
"""


class ModelDatabaseManager:
    """
    Gestionnaire centralisé de la base de données des modèles LLM
    Évite le hardcoding et permet une gestion dynamique
    """

    def __init__(self, database_path: Optional[str] = None) -> None:
        super().__init__()
        """
        Initialise le gestionnaire de base de données

        Args:
            database_path: Chemin vers le fichier YAML de base de données
        """
        if database_path is None:
            # Chemin par défaut relatif au fichier
            current_dir = Path(__file__).parent
            database_path = str(
                current_dir / "../../config/models_database_template.yaml"
            )

        self.database_path = Path(database_path)
        self._database: Optional[Dict[str, Any]] = None
        self._models_cache: Dict[str, Any] = {}
        self._providers_cache: Dict[str, Any] = {}
        self._tools_cache: Dict[str, Any] = {}

    def load_database(self) -> bool:
        """Charge la base de données depuis le fichier YAML"""
        try:
            if not self.database_path.exists():
                logger.error(f"Base de données non trouvée: {self.database_path}")
                return False

            with open(self.database_path, "r", encoding="utf-8") as f:
                self._database = yaml.safe_load(f)

            logger.info(
                f"Base de données chargée: {self._database.get('version', 'unknown')}"
            )
            return True

        except Exception as e:
            logger.error(f"Erreur lors du chargement de la base de données: {e}")
            return False

    def save_database(self) -> bool:
        """Sauvegarde la base de données vers le fichier YAML"""
        try:
            with open(self.database_path, "w", encoding="utf-8") as f:
                yaml.dump(
                    self._database, f, default_flow_style=False, allow_unicode=True
                )

            logger.info("Base de données sauvegardée")
            return True

        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde: {e}")
            return False

    def get_supported_models_for_tool(self, tool_name: str) -> List[ModelInfo]:
        """
        Récupère tous les modèles supportés par un outil spécifique

        Args:
            tool_name: Nom de l'outil (cline, roo_code, kilocode)

        Returns:
            Liste des modèles supportés
        """
        if not self._database:
            self.load_database()

        if not self._database:
            return []

        if tool_name not in self._tools_cache:
            if self._database is None:
                return []
            tool_data = self._database.get("tools", {}).get(tool_name)
            if not tool_data:
                logger.warning(f"Outil non trouvé: {tool_name}")
                return []

            models: List[ModelInfo] = []
            for model_data in tool_data.get("supported_models", []):
                model = ModelInfo(
                    id=model_data["id"],
                    provider=model_data["provider"],
                    family=model_data["family"],
                    context_window=model_data["context_window"],
                    pricing=model_data["pricing"],
                    capabilities=model_data["capabilities"],
                    recommended_for=model_data["recommended_for"],
                    tool_support=[tool_name],
                )
                models.append(model)

            self._tools_cache[tool_name] = models

        return self._tools_cache[tool_name]

    def get_all_models(self) -> List[ModelInfo]:
        """Récupère tous les modèles de tous les outils"""
        if not self._database:
            self.load_database()
            if not self._database:
                return []

        all_models: List[ModelInfo] = []
        seen_models: set[str] = set()

        if self._database is not None:
            for tool_name in self._database.get("tools", {}):
                tool_models = self.get_supported_models_for_tool(tool_name)
                for model in tool_models:
                    model_key = f"{model.provider}:{model.id}"
                    if model_key not in seen_models:
                        # Vérifier si ce modèle est supporté par d'autres outils
                        model.tool_support = self._get_tools_supporting_model(model.id)
                        all_models.append(model)
                        seen_models.add(model_key)

        return all_models

    def _get_tools_supporting_model(self, model_id: str) -> List[str]:
        """Trouve tous les outils qui supportent un modèle spécifique"""
        if not self._database:
            return []

        supporting_tools: List[str] = []

        if self._database is not None:
            for tool_name, tool_data in self._database.get("tools", {}).items():
                for model_data in tool_data.get("supported_models", []):
                    if model_data["id"] == model_id:
                        supporting_tools.append(tool_name)
                        break

        return supporting_tools

    def get_provider_info(self, provider_name: str) -> Optional[ProviderInfo]:
        """Récupère les informations d'un provider"""
        if not self._database:
            self.load_database()
            if not self._database:
                return None

        if provider_name not in self._providers_cache:
            if self._database is None:
                return None
            provider_data = self._database.get("providers", {}).get(provider_name)
            if not provider_data:
                return None

            provider = ProviderInfo(
                name=provider_data["name"],
                website=provider_data["website"],
                api_docs=provider_data["api_docs"],
                models_endpoint=provider_data["models_endpoint"],
                rate_limits=provider_data["rate_limits"],
                pricing_model=provider_data["pricing_model"],
            )

            self._providers_cache[provider_name] = provider

        return self._providers_cache[provider_name]

    def get_recommended_models_for_task(self, task_type: str) -> Dict[str, List[str]]:
        """
        Récupère les modèles recommandés pour un type de tâche

        Args:
            task_type: Type de tâche (code_analysis, code_generation, etc.)

        Returns:
            Dictionnaire avec primary_models, secondary_models, avoid_models
        """
        if not self._database:
            self.load_database()
            if not self._database:
                return {
                    "primary_models": [],
                    "secondary_models": [],
                    "avoid_models": [],
                }

        if self._database is None:
            return {"primary_models": [], "secondary_models": [], "avoid_models": []}
        recommendations = self._database.get("task_recommendations", {}).get(
            task_type, {}
        )
        return {
            "primary_models": recommendations.get("primary_models", []),
            "secondary_models": recommendations.get("secondary_models", []),
            "avoid_models": recommendations.get("avoid_models", []),
        }

    def find_models_by_capability(self, capability: str) -> List[ModelInfo]:
        """Trouve tous les modèles ayant une capacité spécifique"""
        all_models = self.get_all_models()
        return [model for model in all_models if capability in model.capabilities]

    def find_models_by_provider(self, provider: str) -> List[ModelInfo]:
        """Trouve tous les modèles d'un provider spécifique"""
        all_models = self.get_all_models()
        return [model for model in all_models if model.provider == provider]

    def get_models_with_context_window(
        self, min_tokens: int = 0, max_tokens: Optional[int] = None
    ) -> List[ModelInfo]:
        """Trouve les modèles avec une fenêtre de contexte dans une plage donnée"""
        all_models = self.get_all_models()
        if max_tokens is None:
            return [model for model in all_models if model.context_window >= min_tokens]
        return [
            model
            for model in all_models
            if min_tokens <= model.context_window <= max_tokens
        ]

    def get_tools_info(self) -> Dict[str, ToolInfo]:
        """Récupère les informations sur tous les outils"""
        if not self._database:
            self.load_database()
            if not self._database:
                return {}

        tools_info: Dict[str, ToolInfo] = {}
        if self._database is not None:
            for tool_name, tool_data in self._database.get("tools", {}).items():
                models = self.get_supported_models_for_tool(tool_name)
                tools_info[tool_name] = ToolInfo(
                    name=tool_data["name"],
                    website=tool_data["website"],
                    github=tool_data["github"],
                    description=tool_data["description"],
                    supported_models=models,
                )

        return tools_info

    def add_model_to_tool(self, tool_name: str, model_data: Dict[str, Any]) -> bool:
        """Ajoute un modèle à un outil existant"""
        if not self._database:
            self.load_database()
            if not self._database:
                return False

        if tool_name not in self._database.get("tools", {}):
            logger.error(f"Outil non trouvé: {tool_name}")
            return False

        # Vérifier que le modèle n'existe pas déjà
        existing_models = self._database["tools"][tool_name]["supported_models"]
        for existing in existing_models:
            if existing["id"] == model_data["id"]:
                logger.warning(
                    f"Modèle {model_data['id']} existe déjà pour {tool_name}"
                )
                return False

        # Ajouter le modèle
        self._database["tools"][tool_name]["supported_models"].append(model_data)

        # Invalider le cache
        if tool_name in self._tools_cache:
            del self._tools_cache[tool_name]

        logger.info(f"Modèle {model_data['id']} ajouté à {tool_name}")
        return True

    def remove_model_from_tool(self, tool_name: str, model_id: str) -> bool:
        """Supprime un modèle d'un outil"""
        if not self._database:
            self.load_database()
            if not self._database:
                return False

        if tool_name not in self._database.get("tools", {}):
            logger.error(f"Outil non trouvé: {tool_name}")
            return False

        models = self._database["tools"][tool_name]["supported_models"]
        original_length = len(models)

        # Filtrer pour supprimer le modèle
        self._database["tools"][tool_name]["supported_models"] = [
            model for model in models if model["id"] != model_id
        ]

        if (
            len(self._database["tools"][tool_name]["supported_models"])
            < original_length
        ):
            # Invalider le cache
            if tool_name in self._tools_cache:
                del self._tools_cache[tool_name]

            logger.info(f"Modèle {model_id} supprimé de {tool_name}")
            return True
        else:
            logger.warning(f"Modèle {model_id} non trouvé dans {tool_name}")
            return False

    def export_to_json(self, output_path: str) -> bool:
        """Exporte la base de données vers un fichier JSON"""
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(self._database, f, indent=2, ensure_ascii=False)

            logger.info(f"Base de données exportée vers {output_path}")
            return True

        except Exception as e:
            logger.error(f"Erreur lors de l'export JSON: {e}")
            return False

    def get_database_stats(self) -> Dict[str, Any]:
        """Retourne des statistiques sur la base de données"""
        if not self._database:
            self.load_database()
            if not self._database:
                return {
                    "version": "unknown",
                    "total_tools": 0,
                    "total_providers": 0,
                    "total_task_types": 0,
                    "total_models": 0,
                    "models_per_tool": {},
                    "models_per_provider": {},
                }

        stats = {
            "version": self._database.get("version", "unknown"),
            "total_tools": len(self._database.get("tools", {})),
            "total_providers": len(self._database.get("providers", {})),
            "total_task_types": len(self._database.get("task_recommendations", {})),
            "total_models": len(self.get_all_models()),
        }

        # Compter les modèles par outil
        tool_model_counts: Dict[str, int] = {}
        if self._database is not None:
            for tool_name in self._database.get("tools", {}):
                tool_model_counts[tool_name] = len(
                    self.get_supported_models_for_tool(tool_name)
                )

        stats["models_per_tool"] = tool_model_counts

        # Compter les modèles par provider
        provider_counts: Dict[str, int] = {}
        for model in self.get_all_models():
            provider_counts[model.provider] = provider_counts.get(model.provider, 0) + 1

        stats["models_per_provider"] = provider_counts

        return stats

    def validate_database(self) -> List[str]:
        """Valide l'intégrité de la base de données"""
        errors = []

        if not self._database:
            errors.append("Base de données non chargée")
            return errors

        # Vérifier la structure de base
        required_keys = ["tools", "providers", "task_recommendations"]
        for key in required_keys:
            if key not in self._database:
                errors.append(f"Clé requise manquante: {key}")

        # Vérifier que tous les modèles référencés dans les recommandations existent
        all_model_ids = {model.id for model in self.get_all_models()}

        for task_type, recommendations in self._database.get(
            "task_recommendations", {}
        ).items():
            for rec_type in ["primary_models", "secondary_models", "avoid_models"]:
                for model_id in recommendations.get(rec_type, []):
                    if model_id not in all_model_ids:
                        errors.append(
                            f"Modèle {model_id} dans {task_type}.{rec_type} n'existe pas"
                        )

        # Vérifier que tous les providers référencés existent
        all_provider_names = set(self._database.get("providers", {}).keys())

        for model in self.get_all_models():
            if model.provider not in all_provider_names:
                errors.append(
                    f"Provider {model.provider} pour modèle {model.id} n'existe pas"
                )

        return errors
