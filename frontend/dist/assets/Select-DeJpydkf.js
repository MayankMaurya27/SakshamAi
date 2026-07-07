import{f as e,u as t}from"./index-Cu0L7rhl.js";var n=e(`chevron-down`,[[`path`,{d:`m6 9 6 6 6-6`,key:`qrunsl`}]]),r=t();function i({label:e,value:t,onChange:i,options:a=[],placeholder:o=`Select...`,className:s=``,disabled:c=!1}){return(0,r.jsxs)(`div`,{className:`space-y-1.5 ${s}`,children:[e&&(0,r.jsx)(`label`,{className:`block text-xs font-semibold uppercase tracking-wider text-ink-muted`,children:e}),(0,r.jsxs)(`div`,{className:`relative`,children:[(0,r.jsxs)(`select`,{value:t,onChange:i,disabled:c,className:`
            w-full appearance-none
            bg-surface-raised border border-border-strong
            rounded-xl px-4 py-3 pr-10
            text-sm font-medium text-ink
            focus-ring transition-colors
            hover:border-accent/40
            disabled:opacity-50 disabled:cursor-not-allowed
          `,children:[a.length===0&&(0,r.jsx)(`option`,{value:``,children:o}),a.map(e=>{let t=typeof e==`object`?e.value:e;return(0,r.jsx)(`option`,{value:t,children:typeof e==`object`?e.label:e},t)})]}),(0,r.jsx)(n,{size:16,className:`absolute right-3 top-1/2 -translate-y-1/2 text-ink-muted pointer-events-none`})]})]})}export{i as t};