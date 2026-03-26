"""
RAG Database Setup Module
=========================
Creates and populates the ChromaDB vector database
with sample bug history, user stories, and test case data.
"""

import chromadb
from chromadb.utils import embedding_functions
import os

CHROMA_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "chroma_db")
EMBEDDING_MODEL = "all-MiniLM-L6-v2"


def get_chroma_client():
    return chromadb.PersistentClient(path=CHROMA_DB_PATH)


def get_embedding_function():
    return embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=EMBEDDING_MODEL
    )


def setup_bug_history_collection(client, embedding_fn):
    try:
        client.delete_collection("bug_history")
    except:
        pass

    collection = client.create_collection(
        name="bug_history",
        embedding_function=embedding_fn
    )

    bugs = [
        {
            "id": "BUG-2024-001",
            "text": "Cart count not updating after adding items. Severity: High. Module: Shopping Cart. Root Cause: State management issue in frontend.",
            "metadata": {"severity": "high", "module": "shopping_cart", "year": "2024"}
        },
        {
            "id": "BUG-2024-015",
            "text": "Session cart data lost on browser refresh. Severity: Critical. Module: Shopping Cart, Session Management. Root Cause: LocalStorage not syncing with backend.",
            "metadata": {"severity": "critical", "module": "session_management", "year": "2024"}
        },
        {
            "id": "BUG-2024-023",
            "text": "Race condition when adding same item rapidly. Severity: Medium. Module: Shopping Cart API. Root Cause: No debouncing on add-to-cart API calls.",
            "metadata": {"severity": "medium", "module": "shopping_cart_api", "year": "2024"}
        },
        {
            "id": "BUG-2024-045",
            "text": "Price calculation error with quantity greater than 50. Severity: High. Module: Cart Calculations. Root Cause: Integer overflow in legacy calculation code.",
            "metadata": {"severity": "high", "module": "cart_calculations", "year": "2024"}
        },
        {
            "id": "BUG-2024-067",
            "text": "Add to cart fails silently for out-of-stock items. Severity: Medium. Module: Inventory Integration. Root Cause: Missing error handling for inventory check.",
            "metadata": {"severity": "medium", "module": "inventory", "year": "2024"}
        },
        {
            "id": "BUG-2024-089",
            "text": "Guest users could add items without login redirect. Severity: High. Module: Authentication, Shopping Cart. Root Cause: Missing auth middleware on cart endpoints.",
            "metadata": {"severity": "high", "module": "authentication", "year": "2024"}
        },
        {
            "id": "BUG-2023-012",
            "text": "Login page crashes on mobile browsers. Severity: Critical. Module: Authentication. Root Cause: Incompatible CSS causing JS error on Safari.",
            "metadata": {"severity": "critical", "module": "authentication", "year": "2023"}
        },
        {
            "id": "BUG-2023-034",
            "text": "Password reset email not sent for accounts with special characters. Severity: High. Module: Authentication, Email Service. Root Cause: Email regex rejecting valid addresses.",
            "metadata": {"severity": "high", "module": "authentication", "year": "2023"}
        },
        {
            "id": "BUG-2023-056",
            "text": "Payment gateway timeout causing duplicate charges. Severity: Critical. Module: Payment Processing. Root Cause: Missing idempotency key on payment API calls.",
            "metadata": {"severity": "critical", "module": "payment", "year": "2023"}
        },
        {
            "id": "BUG-2023-078",
            "text": "Search results not returning correct products for special characters. Severity: Medium. Module: Search Engine. Root Cause: Query sanitization removing valid search terms.",
            "metadata": {"severity": "medium", "module": "search", "year": "2023"}
        },
        {
            "id": "BUG-2023-091",
            "text": "Product images not loading on slow connections. Severity: Low. Module: Media Service. Root Cause: Missing lazy loading implementation.",
            "metadata": {"severity": "low", "module": "media", "year": "2023"}
        },
        {
            "id": "BUG-2022-007",
            "text": "User profile updates not saving correctly. Severity: High. Module: User Management. Root Cause: Database transaction not committed on profile update.",
            "metadata": {"severity": "high", "module": "user_management", "year": "2022"}
        },
        {
            "id": "BUG-2022-019",
            "text": "Order history pagination broken after 10 pages. Severity: Medium. Module: Order Management. Root Cause: Offset calculation error in pagination logic.",
            "metadata": {"severity": "medium", "module": "order_management", "year": "2022"}
        },
        {
            "id": "BUG-2022-033",
            "text": "Discount codes not applying correctly on sale items. Severity: High. Module: Promotions, Cart Calculations. Root Cause: Discount stacking logic not handling edge cases.",
            "metadata": {"severity": "high", "module": "promotions", "year": "2022"}
        },
        {
            "id": "BUG-2022-055",
            "text": "Notification emails sent multiple times for single event. Severity: Medium. Module: Notification Service. Root Cause: Event listener registered multiple times.",
            "metadata": {"severity": "medium", "module": "notifications", "year": "2022"}
        },
    ]

    collection.add(
        documents=[b["text"] for b in bugs],
        metadatas=[b["metadata"] for b in bugs],
        ids=[b["id"] for b in bugs]
    )
    print(f"   [OK] Bug history collection created with {len(bugs)} bugs")


def setup_user_stories_collection(client, embedding_fn):
    try:
        client.delete_collection("user_stories")
    except:
        pass

    collection = client.create_collection(
        name="user_stories",
        embedding_function=embedding_fn
    )

    stories = [
        {
            "id": "US-001",
            "text": "As a user I want to add products to shopping cart so I can purchase multiple items in one transaction. Acceptance criteria: logged in users only, cart persists across sessions, max 99 units per product.",
            "metadata": {"module": "shopping_cart", "sprint": "sprint_12"}
        },
        {
            "id": "US-002",
            "text": "As a user I want to log in with email and password so I can access my account. Acceptance criteria: email validation, password minimum 8 characters, redirect to home after login.",
            "metadata": {"module": "authentication", "sprint": "sprint_8"}
        },
        {
            "id": "US-003",
            "text": "As a user I want to reset my password via email so I can regain access to my account. Acceptance criteria: email sent within 2 minutes, link expires after 24 hours.",
            "metadata": {"module": "authentication", "sprint": "sprint_9"}
        },
        {
            "id": "US-004",
            "text": "As a user I want to search for products by name or category so I can find items quickly. Acceptance criteria: results appear within 2 seconds, supports partial matches.",
            "metadata": {"module": "search", "sprint": "sprint_10"}
        },
        {
            "id": "US-005",
            "text": "As a user I want to checkout and pay for my cart items so I can complete my purchase. Acceptance criteria: supports credit card and UPI, order confirmation email sent.",
            "metadata": {"module": "payment", "sprint": "sprint_14"}
        },
        {
            "id": "US-006",
            "text": "As a user I want to view my order history so I can track past purchases. Acceptance criteria: shows last 50 orders, filterable by date and status.",
            "metadata": {"module": "order_management", "sprint": "sprint_11"}
        },
        {
            "id": "US-007",
            "text": "As a user I want to apply discount codes at checkout so I can save money on purchases. Acceptance criteria: one code per order, shows discount amount before confirming.",
            "metadata": {"module": "promotions", "sprint": "sprint_13"}
        },
        {
            "id": "US-008",
            "text": "As a user I want to update my profile information so I can keep my details current. Acceptance criteria: can update name, email, phone, changes saved immediately.",
            "metadata": {"module": "user_management", "sprint": "sprint_7"}
        },
    ]

    collection.add(
        documents=[s["text"] for s in stories],
        metadatas=[s["metadata"] for s in stories],
        ids=[s["id"] for s in stories]
    )
    print(f"   [OK] User stories collection created with {len(stories)} stories")


def setup_test_cases_collection(client, embedding_fn):
    try:
        client.delete_collection("test_cases")
    except:
        pass

    collection = client.create_collection(
        name="test_cases",
        embedding_function=embedding_fn
    )

    test_cases = [
        {
            "id": "TC-HIST-001",
            "text": "Test login with valid credentials. Steps: navigate to login, enter valid email and password, click login. Expected: redirected to home page, user name shown in header.",
            "metadata": {"module": "authentication", "priority": "high"}
        },
        {
            "id": "TC-HIST-002",
            "text": "Test login with invalid password. Steps: navigate to login, enter valid email with wrong password, click login. Expected: error message shown, user not logged in.",
            "metadata": {"module": "authentication", "priority": "high"}
        },
        {
            "id": "TC-HIST-003",
            "text": "Test add single item to cart. Steps: login, navigate to product, click add to cart. Expected: cart count increases by 1, confirmation message shown.",
            "metadata": {"module": "shopping_cart", "priority": "high"}
        },
        {
            "id": "TC-HIST-004",
            "text": "Test cart persistence after browser refresh. Steps: login, add item to cart, refresh browser. Expected: cart items still present after refresh.",
            "metadata": {"module": "shopping_cart", "priority": "high"}
        },
        {
            "id": "TC-HIST-005",
            "text": "Test payment with valid credit card. Steps: add item to cart, proceed to checkout, enter valid card details, confirm payment. Expected: order placed, confirmation email received.",
            "metadata": {"module": "payment", "priority": "critical"}
        },
        {
            "id": "TC-HIST-006",
            "text": "Test discount code application. Steps: add item to cart, enter valid discount code at checkout. Expected: discount amount deducted from total.",
            "metadata": {"module": "promotions", "priority": "high"}
        },
        {
            "id": "TC-HIST-007",
            "text": "Test product search with partial name. Steps: type partial product name in search bar. Expected: relevant products shown within 2 seconds.",
            "metadata": {"module": "search", "priority": "medium"}
        },
        {
            "id": "TC-HIST-008",
            "text": "Test out of stock product cannot be added to cart. Steps: navigate to out of stock product page, attempt to add to cart. Expected: add to cart button disabled or error shown.",
            "metadata": {"module": "shopping_cart", "priority": "high"}
        },
    ]

    collection.add(
        documents=[tc["text"] for tc in test_cases],
        metadatas=[tc["metadata"] for tc in test_cases],
        ids=[tc["id"] for tc in test_cases]
    )
    print(f"   [OK] Test cases collection created with {len(test_cases)} test cases")


def initialize_database():
    print("\n" + "="*60)
    print("[SETUP] Initializing RAG Database...")
    print("="*60)
    print(f"\n[+] Database location: {CHROMA_DB_PATH}")

    client = get_chroma_client()
    embedding_fn = get_embedding_function()

    print("\n[+] Creating collections...")
    setup_bug_history_collection(client, embedding_fn)
    setup_user_stories_collection(client, embedding_fn)
    setup_test_cases_collection(client, embedding_fn)

    print("\n" + "="*60)
    print("[DONE] RAG Database initialized successfully!")
    print("="*60)
    print(f"\nDatabase stored at: {CHROMA_DB_PATH}")
    print("You can now run the main application.\n")


if __name__ == "__main__":
    initialize_database()