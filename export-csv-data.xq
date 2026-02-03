import module namespace functx = "http://www.functx.com" at "https://www.datypic.com/xq/functx-1.0.1-doc.xq";

declare variable $doc := fn:doc("./atticus-study-results.xml");

(:These are all the tags added to words:)
declare variable $all-tags := ("tag", "name", "open_class", "Case", "Gender", "NumType", "Number", "PronType", "Aspect", "VerbForm", "Voice", "Mood", "Person", "Tense", "Foreign", "Degree", "Poss", "Reflex", "Polarity", "Abbr")


let $words := $doc//word

let $iter :=
for $w in $words
return $w/@*/node-name()
return fn:distinct-values($iter)

(:let $w := $words[6]
for $item in $w/@*
return <elem>{$item/string(), $item/node-name()}</elem>:)