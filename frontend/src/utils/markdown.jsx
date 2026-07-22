// Minimal Markdown -> React renderer for the report subset backend/reports/report_builder.py
// actually emits: # / ## headings, **bold**, `inline code`, "- " bullet lists,
// "N. " numbered lists, and plain paragraphs. Not a general CommonMark parser -
// the format is fully controlled by our own backend, so a small hand-rolled
// renderer avoids pulling in a Markdown dependency for a fixed, known shape.

// Splits a line into text/bold/code runs and returns React children.
function renderInline(text) {
  const parts = text.split(/(\*\*[^*]+\*\*|`[^`]+`)/g).filter((part) => part !== '')
  return parts.map((part, index) => {
    if (part.startsWith('**') && part.endsWith('**')) {
      return <strong key={index}>{part.slice(2, -2)}</strong>
    }
    if (part.startsWith('`') && part.endsWith('`')) {
      return (
        <code key={index} className="report-doc__inline-code">
          {part.slice(1, -1)}
        </code>
      )
    }
    return part
  })
}

const BULLET_RE = /^-\s+(.*)$/
const NUMBERED_RE = /^(\d+)\.\s+(.*)$/

export function renderReportMarkdown(markdown) {
  if (!markdown) return null
  const lines = markdown.split('\n')
  const blocks = []
  let listBuffer = null // { type: 'ul' | 'ol', items: [] }

  function flushList() {
    if (!listBuffer) return
    const ListTag = listBuffer.type
    blocks.push(
      <ListTag key={`list-${blocks.length}`} className="report-doc__list">
        {listBuffer.items.map((item, index) => (
          <li key={index}>{renderInline(item)}</li>
        ))}
      </ListTag>
    )
    listBuffer = null
  }

  for (const rawLine of lines) {
    const line = rawLine.trimEnd()

    if (line === '') {
      flushList()
      continue
    }

    if (line.startsWith('# ')) {
      flushList()
      blocks.push(<h1 key={blocks.length}>{renderInline(line.slice(2))}</h1>)
      continue
    }
    if (line.startsWith('## ')) {
      flushList()
      blocks.push(<h2 key={blocks.length}>{renderInline(line.slice(3))}</h2>)
      continue
    }

    const bulletMatch = line.match(BULLET_RE)
    if (bulletMatch) {
      if (!listBuffer || listBuffer.type !== 'ul') {
        flushList()
        listBuffer = { type: 'ul', items: [] }
      }
      listBuffer.items.push(bulletMatch[1])
      continue
    }

    const numberedMatch = line.match(NUMBERED_RE)
    if (numberedMatch) {
      if (!listBuffer || listBuffer.type !== 'ol') {
        flushList()
        listBuffer = { type: 'ol', items: [] }
      }
      listBuffer.items.push(numberedMatch[2])
      continue
    }

    flushList()
    // Trailing double-space (Markdown hard line break) becomes a <br/> so
    // the report_id/generated/scenario lines stack the way the source
    // markdown intends instead of running together.
    const isHardBreak = rawLine.endsWith('  ')
    blocks.push(
      <p key={blocks.length} className={isHardBreak ? 'report-doc__line' : undefined}>
        {renderInline(line)}
      </p>
    )
  }
  flushList()

  return blocks
}
