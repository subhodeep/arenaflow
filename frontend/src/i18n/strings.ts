export const strings = {
  en: {
    title: 'ArenaFlow',
    subtitle: 'GenAI stadium operations and fan experience for FIFA World Cup 2026',
    assistant: 'Assistant',
    navigation: 'Navigation',
    accessibility: 'Accessibility',
    transportation: 'Transportation',
    sustainability: 'Sustainability',
    operations: 'Operations',
    submit: 'Get recommendation',
    safety: 'For emergencies, contact venue staff immediately.'
  },
  es: {
    title: 'ArenaFlow',
    subtitle: 'Operaciones de estadio y experiencia de aficionados con GenAI para la Copa Mundial FIFA 2026',
    assistant: 'Asistente',
    navigation: 'Navegación',
    accessibility: 'Accesibilidad',
    transportation: 'Transporte',
    sustainability: 'Sostenibilidad',
    operations: 'Operaciones',
    submit: 'Obtener recomendación',
    safety: 'Para emergencias, contacte al personal del recinto inmediatamente.'
  }
} as const;

export type Locale = keyof typeof strings;

export function getStrings(locale: string) {
  return strings[(locale as Locale) in strings ? (locale as Locale) : 'en'];
}
