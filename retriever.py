"""
RAG Retriever Module
====================
Searches ChromaDB and saves manually entered bugs.
"""

import chromadb
from chromadb.utils import embedding_functions
import os
import re
import datetime
from typing import Dict

CHROMA_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "chroma_db")
EMBEDDING_MODEL = "all-MiniLM-L6-v2"


class RAGRetriever:

    def __init__(self):
        self._client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
        self._embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=EMBEDDING_MODEL
        )

    def _get_collection(self, name: str):
        return self._client.get_collection(
            name=name,
            embedding_function=self._embedding_fn
        )

    def get_relevant_bugs(self, query: str, n_results: int = 5) -> str:
        try:
            collection = self._get_collection("bug_history")
            results = collection.query(query_texts=[query], n_results=n_results)

            if not results["documents"][0]:
                return "No relevant bugs found."

            formatted = "Relevant Historical Bugs:\n\n"
            for i, (doc, metadata) in enumerate(
                zip(results["documents"][0], results["metadatas"][0])
            ):
                formatted += f"Bug {i+1}:\n{doc}\n"
                formatted += f"Severity: {metadata.get('severity', 'unknown').upper()}\n\n"
            return formatted

        except Exception as e:
            return f"Could not retrieve bugs: {str(e)}"

    def get_similar_stories(self, query: str, n_results: int = 3) -> str:
        try:
            collection = self._get_collection("user_stories")
            results = collection.query(query_texts=[query], n_results=n_results)

            if not results["documents"][0]:
                return "No similar stories found."

            formatted = "Similar Past User Stories:\n\n"
            for i, (doc, metadata) in enumerate(
                zip(results["documents"][0], results["metadatas"][0])
            ):
                formatted += f"Story {i+1} (Module: {metadata.get('module', 'unknown')}):\n{doc}\n\n"
            return formatted

        except Exception as e:
            return f"Could not retrieve stories: {str(e)}"

    def get_relevant_test_cases(self, query: str, n_results: int = 3) -> str:
        try:
            collection = self._get_collection("test_cases")
            results = collection.query(query_texts=[query], n_results=n_results)

            if not results["documents"][0]:
                return "No relevant test cases found."

            formatted = "Relevant Past Test Cases:\n\n"
            for i, (doc, metadata) in enumerate(
                zip(results["documents"][0], results["metadatas"][0])
            ):
                formatted += f"Test Case {i+1} (Priority: {metadata.get('priority', 'unknown').upper()}):\n{doc}\n\n"
            return formatted

        except Exception as e:
            return f"Could not retrieve test cases: {str(e)}"

    def get_full_context(self, user_story: str) -> Dict[str, str]:
        """Main method — gets all relevant context for a user story."""
        return {
            "relevant_bugs": self.get_relevant_bugs(user_story),
            "similar_stories": self.get_similar_stories(user_story),
            "relevant_test_cases": self.get_relevant_test_cases(user_story)
        }

    def save_bugs(self, bug_text: str) -> int:
        """
        Save manually entered bugs to database.
        Skips duplicates using content hash.
        Returns number of new bugs saved.
        """
        try:
            collection = self._get_collection("bug_history")
            bug_entries = re.split(r'\n(?=BUG-)', bug_text.strip())
            saved_count = 0

            for entry in bug_entries:
                entry = entry.strip()
                if not entry or len(entry) < 20:
                    continue

                severity = "medium"
                if "critical" in entry.lower():
                    severity = "critical"
                elif "high" in entry.lower():
                    severity = "high"
                elif "low" in entry.lower():
                    severity = "low"

                module = "unknown"
                module_match = re.search(r'Module:\s*(.+)', entry, re.IGNORECASE)
                if module_match:
                    module = module_match.group(1).strip()

                bug_hash = str(abs(hash(entry)) % 10000000)
                bug_id = f"BUG-USER-{bug_hash}"

                try:
                    existing = collection.get(ids=[bug_id])
                    if existing["ids"]:
                        continue
                except:
                    pass

                collection.add(
                    documents=[entry],
                    metadatas=[{
                        "severity": severity,
                        "module": module,
                        "source": "user_input",
                        "year": str(datetime.datetime.now().year)
                    }],
                    ids=[bug_id]
                )
                saved_count += 1

            return saved_count

        except Exception as e:
            print(f"   [WARN] Could not save bugs: {str(e)}")
            return 0