import * as PDFJS from "pdfjs-dist";
import * as PDFWorker from "pdfjs-dist/build/pdf.worker.min";
import 'pdfjs-dist/web/pdf_viewer.css'

export const pdfjsLib = PDFJS;
export const pdfWorkerLib = PDFWorker;
export const { SimpleLinkService } = await import("pdfjs-dist/web/pdf_viewer");
