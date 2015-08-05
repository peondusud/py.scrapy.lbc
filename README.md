# py.scrapy.lbc
LBC crawler using scrapy

cd leboncoin/


scrapy crawl lbc -o output.json

scrapy crawl lbc -o output.json --loglevel INFO --set CONCURRENT_REQUESTS_PER_DOMAIN=8




// check xPATH 

function getElementByXpath(path) {

  var x  = document.evaluate(path, document, null, XPathResult.ORDERED_NODE_ITERATOR_TYPE, null);

  while ((value = x.iterateNext()) != null) {

  console.log(value.value)

  }

}


getElementByXpath('/html/body/div[@id="page_align"]/div[@id="page_width"]/div[@id="ContainerMain"]/nav/ul[@id="paging"]//li[@class="page"]/a/@href');



