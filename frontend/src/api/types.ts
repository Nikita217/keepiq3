export type Task = {
  id: number;
  title: string;
  description: string | null;
  normalized_source_text: string | null;
  due_date: string | null;
  due_time: string | null;
  due_at: string | null;
  reminder_at: string | null;
  is_done: boolean;
  list_id: number | null;
  source_kind: string | null;
  created_at: string;
};

export type InboxItem = {
  id: number;
  source_kind: string;
  raw_text: string | null;
  extracted_text: string | null;
  normalized_text: string | null;
  ai_summary: string | null;
  ai_detected_type: string | null;
  ai_confidence: number | null;
  status: string;
  processing_status: string;
  created_at: string;
};

export type TaskList = {
  id: number;
  title: string;
  description: string | null;
  normalized_source_text: string | null;
  created_at: string;
  updated_at: string;
};

export type TaskListDetail = TaskList & { tasks: Task[] };

export type TodayResponse = {
  overdue: Task[];
  today: Task[];
  inbox_count: number;
};

export type SearchResult = {
  kind: string;
  id: number;
  title: string;
  subtitle: string | null;
  score: number;
  matched_text: string | null;
};

export type SearchResponse = {
  query: string;
  results: SearchResult[];
};

export type AuthResponse = {
  access_token: string;
  token_type: string;
  user: {
    id: number;
    telegram_user_id: number;
    telegram_username: string | null;
    first_name: string | null;
    timezone: string;
  };
};
