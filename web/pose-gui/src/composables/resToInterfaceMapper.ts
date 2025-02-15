import type { AxiosResponse } from 'axios'


export function aboutInterfaceMap(resdata: AxiosResponse | undefined = undefined) {
  const responseData = {
    'detail': '',
  }
  if (resdata !== undefined) {
    responseData.detail = resdata.data.detail ?? '';
  }
  return responseData
}
