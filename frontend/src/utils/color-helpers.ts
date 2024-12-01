export function getQualityColor(value: number): string {
  if (value >= 0.8) return 'bg-green-500';
  if (value >= 0.6) return 'bg-yellow-500';
  return 'bg-red-500';
}

export function getAttentionColor(value: number): string {
  if (value >= 0.8) return 'text-green-600';
  if (value >= 0.6) return 'text-blue-600';
  if (value >= 0.4) return 'text-yellow-600';
  return 'text-red-600';
}