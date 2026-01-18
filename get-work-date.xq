(:Need to go to Perseus DL first, then go to Wikidata using the VIAF number:)

declare namespace tei = "http://www.tei-c.org/ns/1.0";

import module namespace functx = "http://www.functx.com" at "https://www.datypic.com/xq/functx-1.0.1-doc.xq";

(:see this page for more info on querying the Perseus Catalog: https://web.archive.org/web/20240425150208/https://sites.tufts.edu/perseuscatalog/?page_id=542

also see this:
https://web.archive.org/web/20240606170829/https://github.com/projectblacklight/blacklight/wiki/Atom-Responses
:)

declare variable $lat := db:get("canonical-latinLit");

(:
Here is my plan for the process:

Get the URN, probably from the file path in the canonical-latinLit repo

Find the author's authority record based on the URN

Get the VIAF number from the authority record

Go to the author on Wikidata through the VIAF number
:)

declare function local:get-author-id($doc as node())
{
  let $tokenized := fn:tokenize(fn:base-uri($doc), '/')
  return $tokenized[3]
};

(:~
 : Returns the Atom XML from an online query to the Perseus Digital Catalog
 :
 : @author  Matthew DeHass 
 : @version 1.0 
 : @param   $urn a part of the URN for an author or work
 :)
declare function local:retrieve-atom($urn as xs:string)
{
  let $api-call := fn:concat('https://catalog.perseus.org/catalog.atom?q=', $urn, "&amp;search_field=urn")
  return fn:doc($api-call)
};

(:let $rand := random:integer(fn:count($lat) - 1) + 1
return $lat[$rand]/fn:base-uri(.):)

for $doc in $lat
let $title := $doc/tei:TEI/tei:teiHeader/tei:fileDesc/tei:titleStmt/tei:
return $title/text()

