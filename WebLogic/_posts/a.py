import sys

# stdin을 NUL 파일로 리디렉션하여 대화형 입력을 비활성화
#sys.stdin = open('NUL', 'r')

# 터미널에 메시지 출력 비활성화
#sys.stdout = open('NUL', 'w')

# 파일 경로를 슬래시로 표시하거나 역슬래시를 이스케이프 문자로 사용
filePath = "C:\\Users\\Dong-Hyun.KIM\\Desktop\\GoodMorning\\2.-Blog\\dhkim900331.github.io\\WebLogic\\_posts\\0000-00-75-test.md"

# 파일을 읽는다.
with open(filePath, "r", encoding="euc-kr") as f:
  # 모든 줄을 배열로 읽기
  lines = f.readlines()
  
  # 문서 총 길이 = 배열의 전체 길이
  fileTotalLine = len(lines)
  
  # 배열 원소 offset
  offset = 0
  
  # 현재 라인이 공백일 때, 증가하는 변수
  thisNewLine = 0
  
  # 최대 개행 제한 변수
  maxNewLine = 5
  
  # 연속된 개행대신 삽입할 태그
  tagBR = "{{ site.content.br_big }}"
  
  # Frontmatter tag string
  frontmatterTagString = '---'
  
  # Code fence tag string
  codefenceTagString = '```'
  
  # New Line tag string 
  newlineTagString = '\n'
  
  # 변수 디버깅 용도
  print("[DEBUG] Variables start")
  print("[DEBUG] lines : ", lines)
  print("[DEBUG] fileTotalLine :", fileTotalLine)
  print("[DEBUG] thisNewLine : ", thisNewLine)
  print("[DEBUG] maxNewLine : ", maxNewLine)
  print("[DEBUG] tagBR : ", tagBR)
  print("[DEBUG] frontmatterTagString : ", frontmatterTagString)
  print("[DEBUG] codefenceTagString : ", codefenceTagString)
  print("[DEBUG] newlineTagString : ", newlineTagString)
  print("[DEBUG] Variables end")
  
  # 컨텐츠가 들어 있는 배열 원소 하나씩 loop를 돈다.
  while offset < (fileTotalLine - 1):
  
    print("\n")
    print("[DEBUG] 메인 loop 횟수 (offset) : ", offset)
    print("\n")
    
    
    ### Frontmatter 영역을 건너 띄기 위함 ###
    # Frontmatter 시작점을 찾았다.
    if lines[offset].strip()[:3] == frontmatterTagString:
    
      print("\n")
      print("[DEBUG] Frontmatter 시작지점을 찾음.")
      print("[DEBUG} 현재 offset : ", offset)
      print("[DEBUG} 현재 offset 이 가리키는 배열 원소 값(lines[offset]) : ", lines[offset])
      print("\n")
      
      # 이후 연이어 Frontmatter가 있는지 찾기 위한 loop (python은 for range를 마지막-1 까지만 회전한다.)
      for ii in range((offset+1), fileTotalLine):
      
        print("\n")
        print("[DEBUG] Frontmatter 시작점 이후 더 있는지 찾기 위한 loop")
        print("[DEBUG] loop는 %d 부터 %d 까지 실행된다." % (ii, fileTotalLine-1))
        print("[DEBUG} 현재 loop가 가리키는 배열 원소 값(lines[ii]) : ", lines[ii])
        print("\n")
        
        # 연이어 Frontmatter이 발견되었다.
        if lines[ii].strip()[:3] == frontmatterTagString:
        
          # 개행이 발견된 배열 원소 위치 값을 메인 loop의 offset 으로 설정한다. 
          offset = ii
          
          print("\n")
          print("[DEBUG] Frontmatter 을 연이어 발견하였다.")
          print("[DEBUG] 발견된 위치(ii=offset) : ", ii)
          print("\n")
          break
      #################################
  
  
    ### Code fence 영역을 건너 띄기 위함 ###
    # Code fence 시작점을 찾았다.
    if lines[offset].strip()[:3] == codefenceTagString:
    
      print("\n")
      print("[DEBUG] Code fence 시작지점을 찾음.")
      print("[DEBUG} 현재 offset : ", offset)
      print("[DEBUG} 현재 offset 이 가리키는 배열 원소 값(lines[offset]) : ", lines[offset])
      print("\n")
      
      # 이후 연이어 Code fence가 있는지 찾기 위한 loop (python은 for range를 마지막-1 까지만 회전한다.)
      for ii in range((offset+1), fileTotalLine):
      
        print("\n")
        print("[DEBUG] Code fence 시작점 이후 더 있는지 찾기 위한 loop")
        print("[DEBUG] loop는 %d 부터 %d 까지 실행된다." % (ii, fileTotalLine-1))
        print("\n")
        
        # 연이어 Code fence가 발견되었다.
        if lines[ii].strip()[:3] == codefenceTagString:
        
          # Code fence가 발견된 배열 원소 위치 값을 메인 loop의 offset 으로 설정한다. 
          offset = ii
          
          print("\n")
          print("[DEBUG] Code fence 를 연이어 발견하였다.")
          print("[DEBUG] 발견된 위치(ii=offset) : ", ii)
          print("\n")
          break
      #################################


    ### 연속된 개행을 찾기 위함 ###
    # 개행 시작점을 찾았다.
    if lines[offset] == newlineTagString:
    
      # 연속된 개행만큼 누적되는 변수
      # 최초 찾았으므로 1회로 저장
      thisNewLine = 1
      
      print("\n")
      print("[DEBUG] 개행 시작지점을 찾음.")
      print("[DEBUG} 현재 offset : ", offset)
      print("[DEBUG} 현재 offset 이 가리키는 배열 원소 값(lines[offset].strip()) : ", lines[offset].strip())
      print("\n")

      # 이후 연이어 개행이 있는지 찾기 위한 loop (python은 for range를 마지막-1 까지만 회전한다.)
      for ii in range((offset+1), (offset+maxNewLine)):
      
        print("\n")
        print("[DEBUG] 개행 시작점 이후 더 있는지 찾기 위한 loop")
        print("[DEBUG] loop는 %d 부터 %d 까지 실행된다." % (ii, fileTotalLine-1))
        print("\n")
      
        # 연속해서 개행이 인접해 있다.
        if lines[ii] == newlineTagString:
        
          # 개행이 발견된 횟수만큼 누적된다.
          thisNewLine += 1
          
          # 개행이 발견된 배열 원소 위치 값을 메인 loop의 offset 으로 설정한다. 
          offset = ii
          
          print("\n")
          print("[DEBUG] 개행을 연이어 발견하였다.")
          print("[DEBUG] 발견된 위치(ii=offset) : ", ii)
          print("\n")
        
        # 연속해서 개행이 인접하지 않았다.
        else:
          # 검색한 지점이 개행이 아닌 경우이므로, 이전 지점으로 offset 을 설정한다.
          offset = (ii-1)
          
          print("\n")
          print("[DEBUG] 개행이 아닌 다른 요소가 발견되었다.")
          print("[DEBUG} 발견된 원소 값(lines[offset+1].strip()) : ", lines[offset+1].strip())
          print("[DEBUG} 현재 수정된 위치((ii-1)=offset) : ", offset)
          print("\n")
          break
      
      # 최종적으로 찾은 개행이 maxNewLine 만큼 연이어 발견되었다면
      if thisNewLine == maxNewLine:
      
        print("\n")
        print("[DEBUG] 찾은 개행이 %d 에 도달했다." % (thisNewLine))
        print("\n")
      
        # lines 배열에서 maxNewLine 만큼의 개행 원소를 제거한다.
        for ii in range(0, maxNewLine):

          print("\n")
          print("[DEBUG] 배열에서 %d 원소 삭제" % (offset-maxNewLine+1))
          print("[DEBUG] 삭제하려는 배열 원소 값(lines[(offset-maxNewLine+1)].strip()) : ", lines[(offset-maxNewLine+1)].strip())
          print("\n")
          
          # 지우면 뒤의 배열이 앞으로 당겨지므로, 동일한 위치(offset)를 반복하여 지운다.
          # 또한, 현재 offset은 마지막 개행 원소 위치를 가리키므로 앞(-maxNewLine+1) 으로 이동하여 지운다.
          lines.pop(offset-maxNewLine+1)
          
        # tagBR 삽입
        lines.insert(offset, tagBR)
    
        print("\n")
        print("[DEBUG] 배열에 %s 원소 삽입" % (tagBR))
        print("\n")
          
        # lines 배열이 변경되었으므로, 관련된 변수 업데이트
        print("\n")
        print("[DEBUG] 실제 배열 원소가 변경되었으므로 배열 길이를 업데이트하여 loop 횟수가 조정된다.")
        print("[DEBUG] 변경 전(%d) -> 변경 후(%d)" % (fileTotalLine, len(lines)))
        print("\n")
        
        fileTotalLine = len(lines)
        
    # loop의 마지막이므로, 다음 원소 배열 검색을 위해 offset 증가
    offset += 1    
    
  # 결과 확인
  print("lines:", lines)
