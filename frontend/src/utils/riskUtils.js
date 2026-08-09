export function riskClass(level = "") {
  return `risk-${String(level).toLowerCase()}`;
}

export function priorityClass(priority = "") {
  return `priority-${String(priority).toLowerCase()}`;
}