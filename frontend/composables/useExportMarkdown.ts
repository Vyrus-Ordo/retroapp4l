import { unref } from 'vue'
import type { MaybeRef } from '@vueuse/core'
import type { Card, Participant, ActionItem } from '~/utils/types'

export interface ExportMarkdownOptions {
  retro: MaybeRef<{
    title: string
    sprint_name: string | null
    team_key: string
    closed_at: string | null
    description: string | null
  } | null | undefined>
  participants: MaybeRef<Participant[]>
  cards: MaybeRef<Card[]>
  actionItems: MaybeRef<ActionItem[]>
}

export const useExportMarkdown = (options: ExportMarkdownOptions) => {
  const getAuthor = (card: Card) => {
    if (card.is_anonymous) return 'Anonymous'
    return card.author_name || null
  }

  const exportMarkdown = (layout: 'table' | 'sections') => {
    const retro = unref(options.retro)
    const participants = unref(options.participants)
    const cards = unref(options.cards)
    const actionItems = unref(options.actionItems)

    if (!retro) return

    // Formatar data
    let formattedDate = ''
    let safeDate = ''
    if (retro.closed_at) {
      const d = new Date(retro.closed_at)
      const day = String(d.getDate()).padStart(2, '0')
      const month = String(d.getMonth() + 1).padStart(2, '0')
      const year = d.getFullYear()
      formattedDate = `${day}/${month}/${year}`
      safeDate = `${day}-${month}-${year}`
    }

    // Header
    const participantNames = participants.map((p: any) => p.user_name || p.name).join(', ') || '-'
    let md = `# ${retro.title}\n`
    md += `**Sprint:** ${retro.sprint_name || '-'}\n`
    md += `**Time:** ${retro.team_key}\n`
    md += `**Data:** ${formattedDate || '-'}\n`
    md += `**Participantes:** ${participantNames}\n\n`

    if (retro.description) {
      md += `${retro.description}\n\n`
    }

    const columns = [
      { key: 'loved', label: 'Liked' },
      { key: 'loathed', label: 'Loathed' },
      { key: 'longed', label: 'Longed for' },
      { key: 'learned', label: 'Learned' }
    ]

    // Cards
    if (layout === 'sections') {
      columns.forEach(col => {
        md += `## ${col.label}\n\n`
        const colCards = cards.filter(c => c.column === col.key)
        const rootCards = colCards.filter(c => !c.group_parent_id && !c.group)
        
        if (rootCards.length === 0) {
          md += `Nenhum card.\n\n`
        } else {
          rootCards.forEach(card => {
            md += `- ${card.content}\n`
            const author = getAuthor(card)
            if (author) md += `  *— ${author}*\n`
            
            const children = colCards.filter(c => (c.group_parent_id || c.group) === card.id)
            children.forEach(child => {
              md += `  ↳ ${child.content}\n`
              const childAuthor = getAuthor(child)
              if (childAuthor) md += `    *— ${childAuthor}*\n`
            })
          })
          md += `\n`
        }
      })
    } else if (layout === 'table') {
      md += `| ${columns.map(c => c.label).join(' | ')} |\n`
      md += `|---|---|---|---|\n`
      
      const cells = columns.map(col => {
        const colCards = cards.filter(c => c.column === col.key)
        const rootCards = colCards.filter(c => !c.group_parent_id && !c.group)
        
        let cellContent = ""
        rootCards.forEach((card, idx) => {
          if (idx > 0) cellContent += "<br>"
          cellContent += card.content
          const author = getAuthor(card)
          if (author) cellContent += ` *— ${author}*`
          
          const children = colCards.filter(c => (c.group_parent_id || c.group) === card.id)
          children.forEach(child => {
            cellContent += "<br>&nbsp;&nbsp;↳ " + child.content
            const childAuthor = getAuthor(child)
            if (childAuthor) cellContent += ` *— ${childAuthor}*`
          })
        })
        return cellContent || "-"
      })
      
      md += `| ${cells.join(' | ')} |\n\n`
    }

    // Action Items
    md += `## Action Items\n\n`
    if (actionItems.length === 0) {
      md += `Nenhum action item.\n\n`
    } else {
      md += `| Descrição | Responsável | Prazo | Status |\n`
      md += `|---|---|---|---|\n`
      
      const statusMap: Record<string, string> = {
        not_started: 'Não iniciado',
        in_progress: 'Em andamento',
        done: 'Concluído'
      }
      
      actionItems.forEach((item: any) => {
        const desc = item.description || '-'
        const assignee = item.assignee?.user?.name || item.assignee_name || '-'
        let due = '-'
        if (item.due_date) {
          const dDate = new Date(item.due_date)
          due = `${String(dDate.getDate()).padStart(2, '0')}/${String(dDate.getMonth() + 1).padStart(2, '0')}/${dDate.getFullYear()}`
        }
        const status = statusMap[item.status] || item.status || '-'
        
        md += `| ${desc} | ${assignee} | ${due} | ${status} |\n`
      })
      md += `\n`
    }

    md += `---\n*Exportado do RetroApp 4L*\n`

    // Download
    const blob = new Blob([md], { type: 'text/markdown' })
    const url = URL.createObjectURL(blob)
    const sprintOrTitle = retro.sprint_name || retro.title || 'retro'
    const safeName = sprintOrTitle.toLowerCase().replace(/\s+/g, '-')
    const fileName = `retro-${safeName}-${safeDate}.md`
    
    const a = document.createElement('a')
    a.href = url
    a.download = fileName
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  return { exportMarkdown }
}
