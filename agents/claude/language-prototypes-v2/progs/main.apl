Main←{n←⍵ ⋄ {⍵=0:Log'Starting controller service for ',(⍕n),' runs' ⋄ Log'Restarting controller service for run ',(⍕⍵+1),' of ',⍕n}¨¯1+⍳n}
