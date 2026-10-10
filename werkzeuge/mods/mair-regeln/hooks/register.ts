import type { Register } from 'claude-code'

const ORTE = ['aurachtal', 'herzogenaurach', 'erlangen', 'höchstadt', 'hoechstadt', 'hemhofen', 'heroldsberg', 'fürth', 'nürnberg', 'emskirchen', 'neustadt', 'erlenbach']
const BIO = 'Anfrage in 1 Minute: Link in der Bio'

const REGELN = [
  'Mair Gebäudetechnik (Patrick Mair, Aurachtal) – feste Regeln, immer anwenden:',
  '- Antworten Deutsch, kurz, ADHS-freundlich, am Ende Next Steps. Stop-Slop: keine KI-Floskeln, wenige Gedankenstriche.',
  '- Rückfragen nur bei Geld, Senden/Posten an Fremde, Kundendaten, Herstellerbildern. Sonst selbst machen, Fehler selbst prüfen und beheben.',
  '- Videos: immer Thorsten-Stimme (Piper de_DE-thorsten-high, length-scale 1.1), nie stumm, nie gleiches Layout oder gleiche Musik, keine Standbilder über 1 s.',
  '- Captions: Ort im ersten Satz, genau 5 Hashtags (2 davon Orte), Zeile "' + BIO + '". Nie "nur noch X Termine".',
  '- Posting: Mo–Fr 10:00 + optional 17:30 (mind. 6 h Abstand), Wochenende max. 1 Post, Klima-Mittwoch 17:30, Mythos Freitag 10:00.',
  '- Nie fremde Beiträge umlabeln (z. B. Mitbewerber); nur Thema/Format übernehmen. Zahlen nur mit Quelle und Stand-Datum.',
  '- Neue Werkzeuge: Skill-Radar (Mo/Mi/Fr) und mair-skill-finder nutzen; Erkenntnisse in Repo-Dateien (REEL-LABOR.md, SKILL-RADAR.md) festhalten.',
].join('\n')

export function pruefeCaption(text: string): string[] {
  const fehler: string[] = []
  const tags = text.match(/#[\p{L}\p{N}_]+/gu) ?? []
  if (tags.length !== 5) fehler.push(`genau 5 Hashtags nötig (sind ${tags.length})`)
  const ortTags = tags.filter(t => ORTE.some(o => t.toLowerCase().includes(o)))
  if (ortTags.length < 2) fehler.push(`mind. 2 Orts-Hashtags nötig (sind ${ortTags.length})`)
  if (!text.includes(BIO)) fehler.push(`Zeile "${BIO}" fehlt`)
  const ersterSatz = (text.split(/[.!?\n]/)[0] ?? '').toLowerCase()
  if (!ORTE.some(o => ersterSatz.includes(o))) fehler.push('Ort fehlt im ersten Satz')
  if (/nur noch \d+ (freie )?termin/i.test(text)) fehler.push('"nur noch X Termine" ist verboten')
  return fehler
}

function captionAus(info: unknown): { text: string; isStoryOnly: boolean } | null {
  try {
    const o = typeof info === 'string' ? JSON.parse(info) : (info as Record<string, unknown>)
    const text = typeof o?.text === 'string' ? o.text : ''
    const ig = (o?.instagramData ?? {}) as { type?: string }
    const fb = (o?.facebookData ?? {}) as { type?: string }
    const nets = Array.isArray(o?.providers) ? o.providers.map((p: { network?: string }) => p.network) : []
    const isStoryOnly = nets.every((n: string) => (n === 'instagram' && ig.type === 'STORY') || (n === 'facebook' && fb.type === 'STORY'))
    return { text, isStoryOnly }
  } catch {
    return null
  }
}

const POST_TOOLS = ['mcp__Metricool_Social_Media_Management__createScheduledPost', 'mcp__Metricool_Social_Media_Management__updateScheduledPost']

export const register: Register = on => {
  on('prompt.compose', async ($, e, next) => {
    const r = await next(e)
    return { sections: [...r.sections, { id: 'mair:regeln', text: REGELN, scope: 'session' }] }
  })

  for (const tool of POST_TOOLS) {
    on('tool.call', { tool }, ($, e, next) => {
      const c = captionAus((e as unknown as { info?: unknown }).info)
      if (!c || c.isStoryOnly || c.text === '') return next(e)
      const fehler = pruefeCaption(c.text)
      if (fehler.length) {
        $.ui.toast(`Caption-Prüfer: ${fehler.length} Fehler`)
        return { deny: `mair-regeln Caption-Prüfer: ${fehler.join('; ')}. Bitte Caption korrigieren und erneut senden.` }
      }
      return next(e)
    }).catch(($, e, next) => (next.called ? next(e) : next(e)))
  }

  on('tool.call', { tool: 'Bash' }, ($, e, next) => {
    const cmd = e.command
    const forcePush = /git\s+push\b[^\n]*(\s--force\b|\s-f\b|\s--force-with-lease\b)/.test(cmd)
    const rmGefaehrlich = /\brm\s+-[a-zA-Z]*r[a-zA-Z]*f?\b[^\n;&|]*(\s\/(\s|$)|\s~|\/home\/claude\/mair-videos-public-create(\s|\/?$)|\s\.\s*$|\s\*)/.test(cmd)
    if (forcePush || rmGefaehrlich) {
      $.ui.toast('Lösch-Warnung: Befehl gestoppt')
      return { deny: `mair-regeln Lösch-Warnung: "${cmd.slice(0, 80)}" könnte Arbeit unwiderruflich löschen. Erst Patrick fragen oder einen sicheren Weg nehmen.` }
    }
    return next(e)
  })
}
