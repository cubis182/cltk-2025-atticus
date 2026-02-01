import module namespace functx = "http://www.functx.com" at "https://www.datypic.com/xq/functx-1.0.1-doc.xq";

declare variable $doc := fn:doc("./atticus-study-results.xml");

let $words := $doc//word
let $iter :=
for $w in $words
let $element := <elem/>
