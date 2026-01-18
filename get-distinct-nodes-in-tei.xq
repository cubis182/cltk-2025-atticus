declare namespace tei = "http://www.tei-c.org/ns/1.0";

let $doc := fn:doc('C:\Users\T470s\Documents\GitHub\canonical-latinLit\data\phi0959\phi002\phi0959.phi002.perseus-lat2.xml')
let $results :=
for $node in $doc//tei:body//*
return $node/name()
return fn:distinct-values($results)