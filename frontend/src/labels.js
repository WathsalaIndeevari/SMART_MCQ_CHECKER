export function position_to_label_client(position, answerStyle) {
  if (!position) return "—";
  if (answerStyle === "NUMERIC") return String(position);
  return "ABCDE"[position - 1] || String(position);
}
