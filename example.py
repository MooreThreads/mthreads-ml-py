#
# Sample script to demonstrate the usage of MTML API python bindings
#

# To Run:
# $ python ./example.py

from pymtml import *


#
# Converts errors into string messages
#
def handleError(err):
    if err.value == MTML_ERROR_NOT_SUPPORTED:
        return "N/A"
    else:
        return err.__str__()


#######
def deviceQuery():

    strResult = ""
    try:
        #
        # Initialize MTML
        #
        mtmlLibraryInit()

        deviceCount = mtmlLibraryCountDevice()
        strResult += "  <attached_gpus>" + str(deviceCount) + "</attached_gpus>\n"

        for i in range(0, deviceCount):
            handle = mtmlLibraryInitDeviceByIndex(i)

            strResult += '  <gpu id="%s">\n' % i

            try:
                uuid = mtmlDeviceGetUUID(handle)
            except MTMLError as err:
                uuid = handleError(err)

            strResult += "    <uuid>" + uuid + "</uuid>\n"

            try:
                mtLinkSpec = mtmlDeviceGetMtLinkSpec(handle)
            except MTMLError as err:
                mtLinkSpec = handleError(err)
            strResult += "    <mt_link>" + str(mtLinkSpec) + "</mt_link>\n"

            strResult += "  </gpu>\n"

    except MTMLError as err:
        strResult += "example.py: " + err.__str__() + "\n"

    mtmlLibraryShutDown()

    return strResult


# If this is not executed when module is imported
if __name__ == "__main__":
    print(deviceQuery())
