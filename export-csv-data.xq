import module namespace functx = "http://www.functx.com" at "https://www.datypic.com/xq/functx-1.0.1-doc.xq";

declare variable $doc := fn:doc("./atticus-study-results.xml");

declare variable $postag := fn:doc("./postagged_only.xml");

(:These are all the tags added to words:)
declare variable $all-tags := ("title", "path", "tag", "Case", "Gender", "Number", "PronType", "Aspect", "VerbForm", "Voice", "Mood", "Person", "Tense", "Degree", "Polarity");

let $tags := fn:distinct-values($postag//word/*/node-name(.))
let $root :=
<root>
{
  for $word in $postag//word
  return <word>
  {for $t in $tags
  return element {$t} {$word/*[node-name(.) = $t]/text()}}
  </word>
}
</root>
return csv:serialize($root, map{"header":true()})



(:We need the following:)

(:
let $iter :=
for $w in $words
return $w/@*/node-name()
return fn:distinct-values($iter)
:)
(:let $w := $words[6]
for $item in $w/@*
return <elem>{$item/string(), $item/node-name()}</elem>:)