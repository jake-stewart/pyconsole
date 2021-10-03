nnoremap <silent><buffer> <CR> :silent! w!<cr><c-w><c-w><c-c><cr><cr><c-w><c-w>
vnoremap <silent><buffer> <CR> <esc>:silent! '<,'>w!<cr><c-w><c-w><c-c><cr><cr><c-w><c-w>
nnoremap <silent><buffer> <c-c> <c-w><c-w><c-c><c-w><c-w>

command WQ w|qa!
cabbrev <buffer> q qa!
cabbrev <buffer> qa qa!
cabbrev <buffer> wq WQ
cabbrev <buffer> e e!


call feedkeys(":vert term " . b:command . "\<cr>\<c-w>\<c-w>")
echo ""
