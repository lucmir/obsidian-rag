import { ItemView, MarkdownRenderer, WorkspaceLeaf, Notice } from "obsidian";
import type DeepNotesPlugin from "./main";
import type { Source } from "./api-client";

export const VIEW_TYPE = "deep-notes-search";

interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  sources?: Source[];
}

export class DeepNotesSearchView extends ItemView {
  private plugin: DeepNotesPlugin;
  private messages: ChatMessage[] = [];
  private messagesEl!: HTMLElement;
  private inputEl!: HTMLTextAreaElement;
  private sendBtn!: HTMLButtonElement;

  constructor(leaf: WorkspaceLeaf, plugin: DeepNotesPlugin) {
    super(leaf);
    this.plugin = plugin;
  }

  getViewType(): string {
    return VIEW_TYPE;
  }

  getDisplayText(): string {
    return "Deep Notes";
  }

  getIcon(): string {
    return "search";
  }

  async onOpen(): Promise<void> {
    const { contentEl } = this;
    contentEl.empty();
    contentEl.addClass("deep-notes-container");

    // Messages area
    this.messagesEl = contentEl.createDiv({ cls: "deep-notes-messages" });

    // Input area
    const inputArea = contentEl.createDiv({ cls: "deep-notes-input-area" });
    this.inputEl = inputArea.createEl("textarea", {
      attr: { placeholder: "Ask about your notes...", rows: "1" },
    });
    this.sendBtn = inputArea.createEl("button", {
      text: "Send",
      cls: "deep-notes-send-btn",
    });

    this.sendBtn.addEventListener("click", () => this.handleSend());
    this.inputEl.addEventListener("keydown", (e: KeyboardEvent) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        this.handleSend();
      }
    });

    // Header actions
    this.addAction("trash", "Clear chat", () => {
      this.messages = [];
      this.messagesEl.empty();
    });
  }

  private async handleSend(): Promise<void> {
    const question = this.inputEl.value.trim();
    if (!question) return;

    this.inputEl.value = "";

    // Add user message
    this.messages.push({ role: "user", content: question });
    this.renderMessage({ role: "user", content: question });

    // Show thinking indicator
    const thinkingEl = this.messagesEl.createDiv({
      cls: "deep-notes-thinking",
      text: "Thinking...",
    });
    this.scrollToBottom();

    // Build chat history (exclude last user message)
    const history = this.messages.slice(0, -1).map((m) => ({
      role: m.role,
      content: m.content,
    }));

    try {
      const res = await this.plugin.apiClient.query(question, history);
      thinkingEl.remove();

      const assistantMsg: ChatMessage = {
        role: "assistant",
        content: res.answer,
        sources: res.sources,
      };
      this.messages.push(assistantMsg);
      this.renderMessage(assistantMsg);
    } catch (err) {
      thinkingEl.remove();
      new Notice(`Deep Notes: ${err}`);
      const errorMsg: ChatMessage = {
        role: "assistant",
        content: `Error: ${err}`,
      };
      this.messages.push(errorMsg);
      this.renderMessage(errorMsg);
    }
  }

  private renderMessage(msg: ChatMessage): void {
    const wrapper = this.messagesEl.createDiv({
      cls: `deep-notes-message deep-notes-message-${msg.role}`,
    });

    const label = wrapper.createDiv({ cls: "deep-notes-message-label" });
    label.setText(msg.role === "user" ? "You" : "Deep Notes");

    const body = wrapper.createDiv();

    if (msg.role === "assistant") {
      MarkdownRenderer.render(
        this.app,
        msg.content,
        body,
        "",
        this.plugin
      );
    } else {
      body.setText(msg.content);
    }

    // Render sources
    if (msg.sources && msg.sources.length > 0) {
      const sourcesEl = wrapper.createDiv({ cls: "deep-notes-sources" });
      sourcesEl.createDiv({
        cls: "deep-notes-sources-title",
        text: "Sources",
      });
      for (const source of msg.sources) {
        const link = sourcesEl.createEl("a", {
          cls: "deep-notes-source-link",
          text: source.file_name,
        });
        link.createSpan({
          cls: "deep-notes-source-score",
          text: ` (${source.score.toFixed(3)})`,
        });
        link.addEventListener("click", (e) => {
          e.preventDefault();
          this.app.workspace.openLinkText(
            source.file_path.replace(".md", ""),
            "",
            false
          );
        });
      }
    }

    this.scrollToBottom();
  }

  private scrollToBottom(): void {
    this.messagesEl.scrollTop = this.messagesEl.scrollHeight;
  }

  async onClose(): Promise<void> {
    this.contentEl.empty();
  }
}
