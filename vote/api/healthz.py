from fastapi import APIRouter

router = APIRouter()


@router.get('/readiness')
async def ready_probe():
    '''
    Ready probe.
    '''


@router.get('/')
@router.get('/liveness')
async def live_probe():
    '''
    Live probe.
    '''