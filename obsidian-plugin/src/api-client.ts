import { requestUrl } from "obsidian";

export interface Source {
  file_name: string;
  file_path: string;
  text: string;
  score: number;
}

export interface QueryResponse {
  answer: string;
  sources: Source[];
}

export interface IndexResponse {
  count: number;
}

export interface HealthResponse {
  status: string;
}

export class ApiClient {
  constructor(private baseUrl: string, private apiKey: string) {}

  updateConfig(baseUrl: string, apiKey: string) {
    this.baseUrl = baseUrl;
    this.apiKey = apiKey;
  }

  private headers(): Record<string, string> {
    return {
      "Content-Type": "application/json",
      Authorization: `Bearer ${this.apiKey}`,
    };
  }

  async healthCheck(): Promise<HealthResponse> {
    const res = await requestUrl({
      url: `${this.baseUrl}/api/health`,
      method: "GET",
    });
    return res.json;
  }

  async query(
    question: string,
    chatHistory: { role: string; content: string }[]
  ): Promise<QueryResponse> {
    const res = await requestUrl({
      url: `${this.baseUrl}/api/query`,
      method: "POST",
      headers: this.headers(),
      body: JSON.stringify({ question, chat_history: chatHistory }),
    });
    return res.json;
  }

  async indexVault(vaultPath?: string): Promise<IndexResponse> {
    const res = await requestUrl({
      url: `${this.baseUrl}/api/index`,
      method: "POST",
      headers: this.headers(),
      body: JSON.stringify(vaultPath ? { vault_path: vaultPath } : {}),
    });
    return res.json;
  }

  async clearIndex(): Promise<{ status: string }> {
    const res = await requestUrl({
      url: `${this.baseUrl}/api/clear-index`,
      method: "POST",
      headers: this.headers(),
      body: JSON.stringify({}),
    });
    return res.json;
  }
}
