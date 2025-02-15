import type { AboutInterface } from '@/interface/aboutInterface';


export function aboutInterfaceMap(resdata: AboutInterface | undefined = undefined): AboutInterface {
  const responseData: AboutInterface = {
    'detail': '',
  }
  if (resdata !== undefined) {
    responseData.detail = resdata.detail ?? '';
  }
  return responseData
}
