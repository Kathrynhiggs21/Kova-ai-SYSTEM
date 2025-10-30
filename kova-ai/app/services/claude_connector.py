"""
Claude API Connector with Artifacts Support

Provides comprehensive integration with Claude AI including:
- Message API
- Artifacts creation and management
- Code generation
- Document analysis
- Multi-turn conversations
"""

import os
import httpx
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ArtifactType(str, Enum):
    CODE = "code"
    DOCUMENT = "document"
    DIAGRAM = "diagram"
    CONFIG = "config"
    DATA = "data"


class ClaudeConnector:
    """
    Enhanced Claude API connector with artifacts support
    """

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.base_url = "https://api.anthropic.com/v1"
        self.model = "claude-3-sonnet-20240229"
        self.max_tokens = 4096

        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY is required")

    def _get_headers(self) -> Dict[str, str]:
        """Get API request headers"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }

    async def send_message(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        conversation_history: Optional[List[Dict]] = None,
        temperature: float = 1.0,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Send a message to Claude

        Args:
            prompt: User message
            system_prompt: System instructions
            conversation_history: Previous messages
            temperature: Randomness (0-1)
            max_tokens: Maximum response length

        Returns:
            Response with message and metadata
        """
        try:
            messages = conversation_history or []
            messages.append({
                "role": "user",
                "content": prompt
            })

            payload = {
                "model": self.model,
                "max_tokens": max_tokens or self.max_tokens,
                "temperature": temperature,
                "messages": messages
            }

            if system_prompt:
                payload["system"] = system_prompt

            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/messages",
                    headers=self._get_headers(),
                    json=payload
                )

                response.raise_for_status()
                result = response.json()

                return {
                    "success": True,
                    "content": result.get("content", [{}])[0].get("text", ""),
                    "model": result.get("model"),
                    "usage": result.get("usage", {}),
                    "stop_reason": result.get("stop_reason"),
                    "id": result.get("id")
                }

        except httpx.HTTPStatusError as e:
            logger.error(f"Claude API HTTP error: {e}")
            return {
                "success": False,
                "error": str(e),
                "status_code": e.response.status_code
            }
        except Exception as e:
            logger.error(f"Claude API error: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def generate_code(
        self,
        description: str,
        language: str = "python",
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate code using Claude

        Args:
            description: What the code should do
            language: Programming language
            context: Additional context

        Returns:
            Generated code and metadata
        """
        system_prompt = f"""You are an expert {language} programmer. Generate clean,
efficient, well-documented code that follows best practices."""

        prompt = f"""Generate {language} code for the following:

{description}"""

        if context:
            prompt += f"\n\nContext:\n{context}"

        prompt += f"""

Please provide:
1. Complete, working code
2. Comments explaining key parts
3. Usage example if applicable

Format the code in a code block."""

        result = await self.send_message(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=4096
        )

        if result["success"]:
            # Extract code from response
            content = result["content"]
            code = self._extract_code_block(content)

            return {
                "success": True,
                "code": code,
                "full_response": content,
                "language": language,
                "artifact_type": ArtifactType.CODE
            }

        return result

    async def analyze_code(
        self,
        code: str,
        language: str = "python",
        focus: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze code for issues, improvements, and insights

        Args:
            code: Code to analyze
            language: Programming language
            focus: Specific aspect to focus on

        Returns:
            Analysis results
        """
        system_prompt = f"""You are an expert code reviewer specializing in {language}.
Analyze code for bugs, security issues, performance, and best practices."""

        prompt = f"""Analyze this {language} code:

```{language}
{code}
```
"""

        if focus:
            prompt += f"\nFocus on: {focus}\n"

        prompt += """
Provide analysis covering:
1. Potential bugs or issues
2. Security concerns
3. Performance considerations
4. Code quality and best practices
5. Suggestions for improvement
"""

        result = await self.send_message(
            prompt=prompt,
            system_prompt=system_prompt
        )

        return result

    async def analyze_repository(
        self,
        repo_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze a repository's structure and content

        Args:
            repo_data: Repository data from GitHub API

        Returns:
            Repository analysis
        """
        system_prompt = """You are an expert software architect. Analyze repository
structures and provide insights about organization, patterns, and improvements."""

        prompt = f"""Analyze this repository:

{json.dumps(repo_data, indent=2)}

Provide analysis of:
1. Repository structure and organization
2. Technology stack and dependencies
3. Code patterns and architecture
4. Potential improvements
5. Recommendations for development
"""

        result = await self.send_message(
            prompt=prompt,
            system_prompt=system_prompt
        )

        return result

    async def create_artifact(
        self,
        name: str,
        artifact_type: ArtifactType,
        description: str,
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Create an artifact (code, document, diagram, etc.)

        Args:
            name: Artifact name
            artifact_type: Type of artifact
            description: What to create
            context: Additional context

        Returns:
            Created artifact
        """
        if artifact_type == ArtifactType.CODE:
            language = context.get("language", "python") if context else "python"
            return await self.generate_code(description, language, json.dumps(context) if context else None)

        elif artifact_type == ArtifactType.DOCUMENT:
            return await self.generate_document(name, description, context)

        elif artifact_type == ArtifactType.DIAGRAM:
            return await self.generate_diagram(description, context)

        elif artifact_type == ArtifactType.CONFIG:
            return await self.generate_config(description, context)

        else:
            return {"success": False, "error": f"Unsupported artifact type: {artifact_type}"}

    async def generate_document(
        self,
        title: str,
        description: str,
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Generate markdown documentation"""
        system_prompt = """You are an expert technical writer. Create clear,
comprehensive documentation with proper structure and formatting."""

        prompt = f"""Create a markdown document titled "{title}" that covers:

{description}"""

        if context:
            prompt += f"\n\nContext:\n{json.dumps(context, indent=2)}"

        prompt += """

Format as proper markdown with:
- Clear headings
- Code examples where appropriate
- Lists and tables
- Links to resources
"""

        result = await self.send_message(
            prompt=prompt,
            system_prompt=system_prompt
        )

        if result["success"]:
            return {
                "success": True,
                "content": result["content"],
                "title": title,
                "artifact_type": ArtifactType.DOCUMENT
            }

        return result

    async def generate_diagram(
        self,
        description: str,
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Generate Mermaid diagram code"""
        system_prompt = """You are an expert at creating clear, informative diagrams
using Mermaid syntax."""

        prompt = f"""Create a Mermaid diagram for:

{description}"""

        if context:
            prompt += f"\n\nContext:\n{json.dumps(context, indent=2)}"

        prompt += """

Provide:
1. Complete Mermaid code
2. Diagram type explanation
3. How to render it
"""

        result = await self.send_message(
            prompt=prompt,
            system_prompt=system_prompt
        )

        if result["success"]:
            content = result["content"]
            diagram_code = self._extract_code_block(content, "mermaid")

            return {
                "success": True,
                "diagram_code": diagram_code,
                "full_response": content,
                "artifact_type": ArtifactType.DIAGRAM
            }

        return result

    async def generate_config(
        self,
        description: str,
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Generate configuration file"""
        config_format = context.get("format", "json") if context else "json"

        system_prompt = f"""You are an expert at creating well-structured {config_format}
configuration files."""

        prompt = f"""Create a {config_format} configuration for:

{description}"""

        if context:
            prompt += f"\n\nContext:\n{json.dumps(context, indent=2)}"

        prompt += f"""

Provide:
1. Complete {config_format} configuration
2. Explanation of key settings
3. Usage instructions
"""

        result = await self.send_message(
            prompt=prompt,
            system_prompt=system_prompt
        )

        if result["success"]:
            content = result["content"]
            config_code = self._extract_code_block(content, config_format)

            return {
                "success": True,
                "config": config_code,
                "format": config_format,
                "full_response": content,
                "artifact_type": ArtifactType.CONFIG
            }

        return result

    async def multi_turn_conversation(
        self,
        messages: List[str],
        system_prompt: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Conduct a multi-turn conversation

        Args:
            messages: List of user messages
            system_prompt: System instructions

        Returns:
            List of responses
        """
        conversation_history = []
        responses = []

        for message in messages:
            result = await self.send_message(
                prompt=message,
                system_prompt=system_prompt,
                conversation_history=conversation_history
            )

            if result["success"]:
                # Add to history
                conversation_history.append({
                    "role": "user",
                    "content": message
                })
                conversation_history.append({
                    "role": "assistant",
                    "content": result["content"]
                })

            responses.append(result)

        return responses

    def _extract_code_block(self, content: str, language: str = None) -> str:
        """Extract code from markdown code blocks"""
        lines = content.split("\n")
        in_code_block = False
        code_lines = []
        block_language = None

        for line in lines:
            if line.strip().startswith("```"):
                if not in_code_block:
                    # Starting code block
                    in_code_block = True
                    block_language = line.strip()[3:].strip()
                else:
                    # Ending code block
                    if language is None or block_language == language:
                        break
                    else:
                        code_lines = []
                    in_code_block = False
            elif in_code_block:
                code_lines.append(line)

        return "\n".join(code_lines) if code_lines else content


# Convenience functions
async def quick_ask(question: str) -> str:
    """Quick question to Claude"""
    connector = ClaudeConnector()
    result = await connector.send_message(question)
    return result.get("content", "") if result.get("success") else result.get("error", "")


async def quick_code(description: str, language: str = "python") -> str:
    """Quick code generation"""
    connector = ClaudeConnector()
    result = await connector.generate_code(description, language)
    return result.get("code", "") if result.get("success") else result.get("error", "")
