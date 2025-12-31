(:Need to go to Perseus DL first, then go to Wikidata using the VIAF number:)

declare namespace tei = "http://www.tei-c.org/ns/1.0";

(:see this page for more info on querying the Perseus Catalog: https://web.archive.org/web/20240425150208/https://sites.tufts.edu/perseuscatalog/?page_id=542

also see this:
https://web.archive.org/web/20240606170829/https://github.com/projectblacklight/blacklight/wiki/Atom-Responses
:)

declare variable $lat := fn:collection("./../canonical-latinLit");

for $doc in $lat
where $doc/tei:TEI/tei:text/tei:body/tei:div/fn:string(@n) eq ''
return $doc/fn:base-uri(.)

