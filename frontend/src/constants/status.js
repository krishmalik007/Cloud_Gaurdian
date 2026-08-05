export const STATUSES = {
  OPEN: 'OPEN',
  INVESTIGATING: 'INVESTIGATING',
  RESOLVED: 'RESOLVED',
  CLOSED: 'CLOSED',
};

export const STATUS_COLORS = {
  OPEN: {
    bg: 'bg-red/10',
    text: 'text-red',
    border: 'border-red/20',
  },
  INVESTIGATING: {
    bg: 'bg-orange/10',
    text: 'text-orange',
    border: 'border-orange/20',
  },
  RESOLVED: {
    bg: 'bg-green/10',
    text: 'text-green',
    border: 'border-green/20',
  },
  CLOSED: {
    bg: 'bg-text-muted/10',
    text: 'text-text-secondary',
    border: 'border-border-color',
  },
};
