declare namespace tei = "http://www.tei-c.org/ns/1.0";


(:let $doc := fn:doc('C:\Users\T470s\Documents\GitHub\canonical-latinLit\data\phi0959\phi002\phi0959.phi002.perseus-lat2.xml'):)

//*[fn:boolean(./tei:abbr)]

(:
let $doc := fn:doc("C:/Users/T470s/Documents/xml_test.xml")
let $select := $doc//*
return functx:atomic-type($select[3]/text()):)