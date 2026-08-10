An AI-powered customer support backend and dashboard that connects social messaging channels to a shared RAG + LLM pipeline.

The current V1 demo supports **Facebook Messenger and Instagram as independent channels**, while storing conversations in a shared database and exposing analytics through a Streamlit dashboard.

---

## 🚀 Current Features

### Multi-Channel Messaging

- 💬 Facebook Messenger integration
- 📸 Instagram Business integration
- Independent channel connections
- Webhook-based message reception
- AI-generated responses sent directly back to customers

Facebook and Instagram are treated as separate channels. A client can connect either one, or both.

### 🤖 AI Customer Support

Incoming messages are processed through the same AI pipeline regardless of channel.

The system currently supports:

- Intent classification
- Sentiment analysis
- Retrieval-Augmented Generation (RAG)
- Knowledge-base-grounded responses
- Conversation memory
- LLM-generated customer responses

### 🧠 Knowledge Base

The AI can retrieve information from the configured knowledge base before generating a response.

This allows responses to be grounded in company-specific information rather than relying solely on the LLM's general knowledge.

### 💾 Conversation Storage

Facebook Messenger and Instagram conversations are stored in the same SQLite database.

Each new conversation records its originating platform:

```text
instagram
messenger
```

Older conversations created before platform tracking was introduced are preserved and displayed as:

```text
unknown
```

### 📊 Analytics Dashboard

The Streamlit dashboard currently provides:

- Total messages
- Unique customers
- Sentiment distribution
- Intent distribution
- Recent conversations
- AI replies
- Channel/platform statistics
- Instagram vs. Messenger filtering
- Conversation search
- Intent filtering
- Sentiment filtering
- CSV conversation export

---

## 🏗️ Architecture

```text
                    ┌─────────────────┐
                    │    Instagram    │
                    │    Business     │
                    └────────┬────────┘
                             │
                          Webhook
                             │
                             ▼
                    ┌─────────────────┐
                    │                 │
                    │   FastAPI      │
                    │    Backend     │
                    │                 │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
           Intent        Sentiment        RAG
        Classification   Analysis     Knowledge Base
              │              │              │
              └──────────────┼──────────────┘
                             │
                             ▼
                           LLM
                             │
                             ▼
                    ┌─────────────────┐
                    │  Conversation   │
                    │    Database     │
                    └────────┬────────┘
                             │
              ┌──────────────┴──────────────┐
              │                             │
              ▼                             ▼
       Instagram Reply              Messenger Reply


                    ┌─────────────────┐
                    │    Streamlit    │
                    │    Dashboard    │
                    └─────────────────┘
```

Facebook Messenger follows the same backend pipeline and is handled as a separate platform.

---

## 📁 Project Structure

```text
.
├── app.py
├── dashboard.py
├── api.py
├── components.py
├── utils.py
│
├── routes/
│   ├── facebook.py
│   ├── instagram.py
│   ├── messenger.py
│   └── analytics.py
│
├── services/
│   ├── config.py
│   ├── facebook_service.py
│   ├── instagram_service.py
│   ├── analytics_service.py
│   ├── rag_service.py
│   └── ...
│
├── rag/
│   └── ...
│
├── conversations.db
├── .env
└── README.md
```

---

## 🔌 API Endpoints

### Facebook Messenger

```text
POST /messenger/webhook
```

Receives incoming Messenger messages and sends AI-generated responses.

### Instagram

```text
GET  /instagram/login
GET  /instagram/callback
GET  /instagram/me

POST /instagram/webhook
POST /instagram/subscribe
```

Handles Instagram authentication, account information, webhook subscriptions, incoming messages, and replies.

### Analytics

```text
GET /analytics/messages
GET /analytics/users
GET /analytics/sentiment
GET /analytics/intents
GET /analytics/platforms
GET /analytics/recent
```

---

## 🖥️ Dashboard

Run the Streamlit dashboard with:

```bash
streamlit run dashboard.py
```

The dashboard provides a unified view of conversations while allowing filtering by:

- Instagram
- Facebook Messenger
- Intent
- Sentiment
- Search term

---

## ⚙️ Running the Backend

Start FastAPI with:

```bash
python -m uv run uvicorn app:app --reload
```

The API documentation is available at:

```text
http://127.0.0.1:8000/docs
```

---

## 🔐 Environment Variables

Credentials are stored in `.env` and should **never be committed to Git**.

The application uses environment variables for:

- Meta application credentials
- Facebook access tokens
- Instagram credentials
- Webhook verification
- Graph API configuration
- OpenAI API key

Example structure:

```env
META_APP_ID=...
META_APP_SECRET=...

ACCESS_TOKEN=...
PAGE_ID=...

FACEBOOK_REDIRECT_URI=...

INSTAGRAM_APP_ID=...
INSTAGRAM_APP_SECRET=...
INSTAGRAM_ACCESS_TOKEN=...
INSTAGRAM_USER_ID=...
INSTAGRAM_REDIRECT_URI=...

VERIFY_TOKEN=...

OPENAI_API_KEY=...

GRAPH_API_VERSION=v25.0
```

---

## 🛣️ Roadmap

The current implementation is a working V1 demo.

Planned improvements include:

- [ ] Robust token lifecycle / expiration handling
- [ ] Client-facing channel connection UI
- [ ] Instagram/Facebook connection management
- [ ] More advanced analytics
- [ ] Improved dashboard UI/UX
- [ ] Additional messaging channels
- [ ] Production deployment
- [ ] Multi-client / multi-tenant support

---

## 🎯 V1 Design Principle

The system is designed around a **shared AI support backend with independent communication channels**.

Clients should not be required to connect Facebook in order to use Instagram, or Instagram in order to use Facebook.

Instead:

```text
Client
  │
  ├── Instagram ────────┐
  │                      │
  └── Messenger ────────┤
                         ▼
                    Shared AI
                    Support
                    Backend
                         │
                         ▼
                   Knowledge Base
                         │
                         ▼
                    Conversation
                      History
```

This allows additional channels to be added later without redesigning the core AI support system.