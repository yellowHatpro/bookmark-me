import PuppeteerHTMLPDF from "puppeteer-html-pdf";


class URLToPDFDownloader {
    htmlToPDFConvertor: PuppeteerHTMLPDF
    downloadLocation: string


    constructor(downloadLocation: string) {
        this.htmlToPDFConvertor = new PuppeteerHTMLPDF()
        this.htmlToPDFConvertor.setOptions({format: "A3"})
        this.downloadLocation = downloadLocation
    }
    async download(url: string){

    }
}