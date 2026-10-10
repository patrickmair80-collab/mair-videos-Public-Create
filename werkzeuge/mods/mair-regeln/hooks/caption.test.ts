import { test, expect } from 'claude-code/testing'
import { pruefeCaption } from './register'

test('gute Caption besteht', () => {
  const t = 'Aurachtal, Herzogenaurach: Neue Regeln.\n\nAnfrage in 1 Minute: Link in der Bio\n\n#Aurachtal #Herzogenaurach #Photovoltaik #Wärmepumpe #EEG2027'
  expect(pruefeCaption(t)).toEqual([])
})

test('fehlende Bio-Zeile und Terminzahl werden erkannt', () => {
  const t = 'Erlangen: Nur noch 3 Termine frei! #Erlangen #Heizung'
  const f = pruefeCaption(t)
  expect(f.length).toBeGreaterThan(2)
})
