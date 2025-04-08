export interface Source {
  title: string;
  content_preview: string;
}

export interface Message {
  text: string;
  isUser: boolean;
  sources?: Source[];
}

export interface QueryResponse {
  answer: string;
  sources: Source[];
}

export interface DocumentResponse {
  id: string;
  title: string;
  content: string;
}
